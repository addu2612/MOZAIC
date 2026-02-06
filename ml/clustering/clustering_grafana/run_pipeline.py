import argparse
import json
import os
import random
import time
from collections import deque
from typing import Deque, Dict, List

import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from tqdm import tqdm
except Exception:  # pragma: no cover - optional
    tqdm = None

import numpy as np

from clustering_common.io import read_jsonl, write_jsonl
from clustering_common.text import normalize_text
from clustering_common.embeddings import embed_texts
from clustering_common.cluster import run_hdbscan, top_terms_by_cluster
from clustering_common.ollama_label import label_clusters
from clustering_common.severity import grafana_severity


def build_text(row: Dict, context: List[str]) -> str:
    context_str = " | ".join(context) if context else ""
    parts = [
        "source=grafana",
        f"dashboard={row.get('dashboard','')}",
        f"panel={row.get('panel','')}",
        f"service={row.get('service','')}",
        f"value={row.get('value','')}",
        f"unit={row.get('unit','')}",
        f"environment={row.get('environment','')}",
        f"cluster={row.get('cluster','')}",
        f"datasource={row.get('datasource','')}",
        f"query={row.get('query','')}",
        f"panel_type={row.get('metadata', {}).get('panel_type', '')}",
    ]
    if context_str:
        parts.append(f"context={context_str}")
    return normalize_text(" | ".join(parts))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output_dir", default="output")
    parser.add_argument("--model", default="sentence-transformers/all-MiniLM-L6-v2")
    parser.add_argument("--batch_size", type=int, default=64)
    parser.add_argument("--min_cluster_size", type=int, default=15)
    parser.add_argument("--min_samples", type=int, default=5)
    parser.add_argument("--fast_mode", action="store_true")
    parser.add_argument("--pca_dims", type=int, default=50)
    parser.add_argument("--label_with_ollama", action="store_true")
    parser.add_argument("--ollama_model", default="llama3.2:3b")
    parser.add_argument("--include_normal_sample", type=int, default=0)
    parser.add_argument("--sample_size", type=int, default=0)
    parser.add_argument("--sample_seed", type=int, default=42)
    parser.add_argument("--cluster_sample_size", type=int, default=5)
    parser.add_argument("--context_points", type=int, default=0)
    parser.add_argument("--max_label_clusters", type=int, default=100)
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    rows: List[Dict] = []
    normal_pool: List[Dict] = []
    history: Dict[str, Deque[str]] = {}
    iterable = read_jsonl(args.input)
    if tqdm is not None:
        iterable = tqdm(iterable, desc="Loading grafana logs")
    for row in iterable:
        key = f"{row.get('dashboard','')}::{row.get('panel','')}::{row.get('service','')}"
        if args.context_points > 0:
            history.setdefault(key, deque(maxlen=args.context_points))
        if row.get("is_anomaly"):
            context = list(history.get(key, []))
            row["_context"] = context
            rows.append(row)
        else:
            normal_pool.append(row)
        if args.context_points > 0:
            history[key].append(f"{row.get('timestamp','')} {row.get('value','')} {row.get('unit','')}")

    if args.include_normal_sample > 0:
        rows.extend(normal_pool[: args.include_normal_sample])

    if args.sample_size and args.sample_size < len(rows):
        rng = random.Random(args.sample_seed)
        rows = rng.sample(rows, args.sample_size)

    processed = []
    texts = []
    row_iter = rows
    if tqdm is not None:
        row_iter = tqdm(rows, desc="Preprocessing")
    for row in row_iter:
        text = build_text(row, row.get("_context", []))
        texts.append(text)
        processed.append(
            {
                "timestamp": row.get("timestamp"),
                "dashboard": row.get("dashboard"),
                "panel": row.get("panel"),
                "service": row.get("service"),
                "value": row.get("value"),
                "unit": row.get("unit"),
                "environment": row.get("environment"),
                "cluster": row.get("cluster"),
                "datasource": row.get("datasource"),
                "query": row.get("query"),
                "anomaly_type": row.get("anomaly_type"),
                "severity": grafana_severity(row.get("anomaly_type")),
                "text": text,
            }
        )

    write_jsonl(os.path.join(args.output_dir, "grafana_preprocessed.jsonl"), processed)

    embeddings = embed_texts(texts, args.model, batch_size=args.batch_size)
    np.save(os.path.join(args.output_dir, "grafana_embeddings.npy"), embeddings)

    print("Clustering with HDBSCAN... this can take a while on large datasets.")
    start = time.time()
    labels = run_hdbscan(
        embeddings,
        min_cluster_size=args.min_cluster_size,
        min_samples=args.min_samples,
        fast_mode=args.fast_mode,
        pca_dims=args.pca_dims,
    )
    print(f"Clustering done in {time.time() - start:.1f}s")
    top_terms = top_terms_by_cluster(texts, labels)

    cluster_samples = {}
    cluster_ids = sorted(set(labels))
    if tqdm is not None:
        cluster_ids = tqdm(cluster_ids, desc="Collecting cluster samples")
    for cluster_id in cluster_ids:
        if cluster_id == -1:
            continue
        idx = [i for i, label in enumerate(labels) if label == cluster_id]
        if not idx:
            continue
        cluster_samples[int(cluster_id)] = [processed[i] for i in idx[: args.cluster_sample_size]]

    cluster_names = {}
    if args.label_with_ollama:
        sizes = {}
        for label in labels:
            if label == -1:
                continue
            sizes[int(label)] = sizes.get(int(label), 0) + 1
        sorted_ids = sorted(sizes.keys(), key=lambda k: sizes[k], reverse=True)
        if args.max_label_clusters > 0:
            sorted_ids = sorted_ids[: args.max_label_clusters]
        limited_terms = {k: top_terms[k] for k in sorted_ids if k in top_terms}
        cluster_names = label_clusters(limited_terms, args.ollama_model)

    top_terms = {str(k): v for k, v in top_terms.items()}
    cluster_names = {str(k): v for k, v in cluster_names.items()}
    cluster_samples = {str(k): v for k, v in cluster_samples.items()}

    with open(os.path.join(args.output_dir, "grafana_clusters.json"), "w", encoding="utf-8") as f:
        json.dump(
            {
                "labels": labels.tolist(),
                "top_terms": top_terms,
                "cluster_names": cluster_names,
                "cluster_samples": cluster_samples,
            },
            f,
            indent=2,
            ensure_ascii=True,
        )


if __name__ == "__main__":
    main()
