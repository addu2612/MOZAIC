from typing import Dict, List

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
import hdbscan


def run_hdbscan(
    embeddings: np.ndarray,
    min_cluster_size: int = 10,
    min_samples: int = 5,
    fast_mode: bool = False,
    pca_dims: int = 50,
) -> np.ndarray:
    if fast_mode and embeddings.shape[1] > pca_dims:
        pca = PCA(n_components=pca_dims, random_state=42)
        embeddings = pca.fit_transform(embeddings)
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=min_cluster_size,
        min_samples=min_samples,
        metric="euclidean",
        cluster_selection_method="eom",
    )
    return clusterer.fit_predict(embeddings)


def top_terms_by_cluster(texts: List[str], labels: np.ndarray, top_k: int = 10) -> Dict[int, List[str]]:
    vectorizer = TfidfVectorizer(max_features=20000, ngram_range=(1, 2))
    tfidf = vectorizer.fit_transform(texts)
    feature_names = np.array(vectorizer.get_feature_names_out())

    results: Dict[int, List[str]] = {}
    for label in sorted(set(labels)):
        if label == -1:
            continue
        idx = np.where(labels == label)[0]
        if idx.size == 0:
            continue
        cluster_tfidf = tfidf[idx].mean(axis=0)
        cluster_tfidf = np.asarray(cluster_tfidf).ravel()
        top_idx = cluster_tfidf.argsort()[-top_k:][::-1]
        results[label] = feature_names[top_idx].tolist()
    return results
