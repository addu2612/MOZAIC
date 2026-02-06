from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer


def embed_texts(texts: List[str], model_name: str, batch_size: int = 64) -> np.ndarray:
    model = SentenceTransformer(model_name)
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=True,
        normalize_embeddings=True,
    )
    return np.asarray(embeddings, dtype="float32")
