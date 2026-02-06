import argparse
import json
import os
import warnings
from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler, normalize
from sklearn.manifold import TSNE
from sklearn.metrics import (
    calinski_harabasz_score,
    davies_bouldin_score,
    silhouette_score,
)

try:
    import umap  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    umap = None


def load_labels(path: str) -> np.ndarray:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return np.array(data.get("labels", []), dtype=int)


def load_embeddings(path: str) -> np.ndarray:
    return np.load(path)


def load_rows(path: str) -> List[Dict]:
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def cluster_size_table(labels: np.ndarray) -> Dict[str, int]:
    counts = {}
    for label in labels:
        counts[str(label)] = counts.get(str(label), 0) + 1
    return dict(sorted(counts.items(), key=lambda x: int(x[0])))


def safe_metric(fn, embeddings, labels):
    unique = set(labels)
    if len(unique) < 2:
        return None
    if -1 in unique and len(unique) == 2:
        return None
    return fn(embeddings, labels)


def as_float(value):
    if value is None:
        return None
    try:
        return float(value)
    except Exception:
        return None


def to_jsonable(obj):
    if isinstance(obj, (np.integer, np.floating)):
        return obj.item()
    if isinstance(obj, dict):
        return {str(k): to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_jsonable(v) for v in obj]
    return obj


def make_plots(
    output_dir: str,
    embeddings: np.ndarray,
    labels: np.ndarray,
    plot_umap: bool,
    plot_tsne: bool,
    plot_sample_size: int,
) -> None:
    warnings.filterwarnings("ignore")
    np.seterr(all="ignore")
    os.makedirs(output_dir, exist_ok=True)
    embeddings = np.nan_to_num(embeddings, nan=0.0, posinf=1.0, neginf=-1.0)
    embeddings = np.clip(embeddings, -1.0, 1.0)
    embeddings = normalize(embeddings, norm="l2")

    if plot_sample_size and embeddings.shape[0] > plot_sample_size:
        rng = np.random.default_rng(42)
        idx = rng.choice(embeddings.shape[0], size=plot_sample_size, replace=False)
        embeddings = embeddings[idx]
        labels = labels[idx]

    # Cluster size bar chart
    labels_list = labels.tolist()
    unique = sorted(set(labels_list))
    sizes = [labels_list.count(l) for l in unique]

    plt.figure(figsize=(10, 4))
    plt.bar([str(l) for l in unique], sizes)
    plt.title("Cluster Sizes")
    plt.xlabel("Cluster ID")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "cluster_sizes.png"), dpi=160)
    plt.close()

    # 2D PCA scatter
    scaler = StandardScaler()
    emb_scaled = scaler.fit_transform(embeddings)
    pca = PCA(n_components=2, svd_solver="full")
    reduced = pca.fit_transform(emb_scaled)
    plt.figure(figsize=(6, 5))
    plt.scatter(reduced[:, 0], reduced[:, 1], c=labels, s=6, cmap="tab20")
    plt.title("PCA Projection (Colored by Cluster)")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "pca_clusters.png"), dpi=160)
    plt.close()

    if plot_umap and umap is not None:
        reducer = umap.UMAP(n_components=2, random_state=42, n_neighbors=15, min_dist=0.1)
        reduced = reducer.fit_transform(emb_scaled)
        plt.figure(figsize=(6, 5))
        plt.scatter(reduced[:, 0], reduced[:, 1], c=labels, s=6, cmap="tab20")
        plt.title("UMAP Projection (Colored by Cluster)")
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "umap_clusters.png"), dpi=160)
        plt.close()

    if plot_tsne:
        reducer = TSNE(n_components=2, perplexity=30, random_state=42, init="pca")
        reduced = reducer.fit_transform(emb_scaled)
        plt.figure(figsize=(6, 5))
        plt.scatter(reduced[:, 0], reduced[:, 1], c=labels, s=6, cmap="tab20")
        plt.title("t-SNE Projection (Colored by Cluster)")
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "tsne_clusters.png"), dpi=160)
        plt.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--embeddings", required=True)
    parser.add_argument("--clusters", required=True)
    parser.add_argument("--preprocessed", required=True)
    parser.add_argument("--output_dir", required=True)
    parser.add_argument("--plot_umap", action="store_true")
    parser.add_argument("--plot_tsne", action="store_true")
    parser.add_argument("--plot_sample_size", type=int, default=5000)
    parser.add_argument("--metric_sample_size", type=int, default=20000)
    parser.add_argument("--skip_metrics", action="store_true")
    parser.add_argument("--skip_plots", action="store_true")
    args = parser.parse_args()

    embeddings = load_embeddings(args.embeddings).astype("float64")
    embeddings = np.nan_to_num(embeddings, nan=0.0, posinf=1.0, neginf=-1.0)
    embeddings = np.clip(embeddings, -1.0, 1.0)
    embeddings = normalize(embeddings, norm="l2")
    labels = load_labels(args.clusters)
    rows = load_rows(args.preprocessed)

    finite_mask = np.isfinite(embeddings).all(axis=1)
    if not finite_mask.all():
        embeddings = embeddings[finite_mask]
        labels = labels[finite_mask]

    # Sample for expensive metrics to avoid long runtimes
    if args.metric_sample_size and embeddings.shape[0] > args.metric_sample_size:
        rng = np.random.default_rng(42)
        idx = rng.choice(embeddings.shape[0], size=args.metric_sample_size, replace=False)
        emb_metrics = embeddings[idx]
        labels_metrics = labels[idx]
    else:
        emb_metrics = embeddings
        labels_metrics = labels

    if args.skip_metrics:
        metrics = {
            "silhouette_score": None,
            "davies_bouldin_index": None,
            "calinski_harabasz_index": None,
            "num_points": int(len(labels)),
            "num_clusters": int(len(set(labels)) - (1 if -1 in set(labels) else 0)),
            "num_noise": int(np.sum(labels == -1)),
        }
    else:
        metrics = {
            "silhouette_score": as_float(safe_metric(silhouette_score, emb_metrics, labels_metrics)),
            "davies_bouldin_index": as_float(safe_metric(davies_bouldin_score, emb_metrics, labels_metrics)),
            "calinski_harabasz_index": as_float(safe_metric(calinski_harabasz_score, emb_metrics, labels_metrics)),
            "num_points": int(len(labels)),
            "num_clusters": int(len(set(labels)) - (1 if -1 in set(labels) else 0)),
            "num_noise": int(np.sum(labels == -1)),
        }

    sizes = cluster_size_table(labels)

    severity_counts = {}
    for row in rows:
        severity = row.get("severity", "unknown")
        severity_counts[severity] = severity_counts.get(severity, 0) + 1

    os.makedirs(args.output_dir, exist_ok=True)
    with open(os.path.join(args.output_dir, "metrics.json"), "w", encoding="utf-8") as f:
        payload = {
            "metrics": metrics,
            "cluster_sizes": sizes,
            "severity_counts": severity_counts,
        }
        json.dump(to_jsonable(payload), f, indent=2, ensure_ascii=True)

    if not args.skip_plots:
        make_plots(
            args.output_dir,
            embeddings,
            labels,
            args.plot_umap,
            args.plot_tsne,
            args.plot_sample_size,
        )


if __name__ == "__main__":
    main()
