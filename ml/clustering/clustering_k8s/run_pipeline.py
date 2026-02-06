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
from clustering_common.text import normalize_text, flatten_metadata
from clustering_common.embeddings import embed_texts
from clustering_common.cluster import run_hdbscan, top_terms_by_cluster
from clustering_common.ollama_label import label_clusters
from clustering_common.severity import k8s_severity


def build_text(row: Dict, context: List[str]) -> str:
    context_str = " | ".join(context) if context else ""
    parts = [
        "source=k8s",
        f"level={row.get('level','')}",
        f"component={row.get('component','')}",
        f"namespace={row.get('namespace','')}",
        f"message={row.get('message','')}",
        f"error_type={row.get('error_type','')}",
        f"metadata={flatten_metadata(row.get('metadata', {}))}",
    ]
    if context_str:
        parts.append(f"context={context_str}")
    return normalize_text(" | ".join(parts))


def context_key(row: Dict, scope: str) -> str:
    component = row.get("component", "")
    namespace = row.get("namespace", "")
    if scope == "component":
        return component
    if scope == "namespace":
        return namespace
    return f"{component}::{namespace}"


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
    parser.add_argument("--level", default="ERROR")
    parser.add_argument("--sample_size", type=int, default=0)
    parser.add_argument("--sample_seed", type=int, default=42)
    parser.add_argument("--cluster_sample_size", type=int, default=5)
    parser.add_argument("--context_lines", type=int, default=0)
    parser.add_argument("--context_scope", default="component_namespace", choices=["component", "namespace", "component_namespace"])
    parser.add_argument("--max_label_clusters", type=int, default=100)
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    rows: List[Dict] = []
    history: Dict[str, Deque[str]] = {}
    iterable = read_jsonl(args.input)
    if tqdm is not None:
        iterable = tqdm(iterable, desc="Loading k8s logs")
    for row in iterable:
        key = context_key(row, args.context_scope)
        if args.context_lines > 0:
            history.setdefault(key, deque(maxlen=args.context_lines))
        if row.get("level") == args.level:
            context = list(history.get(key, []))
            row["_context"] = context
            rows.append(row)
        if args.context_lines > 0:
            msg = f"{row.get('level','')} {row.get('message','')}"
            history[key].append(msg)

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
                "level": row.get("level"),
                "component": row.get("component"),
                "namespace": row.get("namespace"),
                "message": row.get("message"),
                "error_type": row.get("error_type"),
                "severity": k8s_severity(row.get("error_type")),
                "text": text,
            }
        )

    write_jsonl(os.path.join(args.output_dir, "k8s_preprocessed.jsonl"), processed)

    embeddings = embed_texts(texts, args.model, batch_size=args.batch_size)
    np.save(os.path.join(args.output_dir, "k8s_embeddings.npy"), embeddings)

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

    with open(os.path.join(args.output_dir, "k8s_clusters.json"), "w", encoding="utf-8") as f:
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
