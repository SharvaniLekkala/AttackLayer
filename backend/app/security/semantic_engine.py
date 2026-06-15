"""
Semantic engine — pluggable similarity via neurosymbolic module.
"""

import numpy as np

from app.neurosymbolic.embeddings import get_embedding
from app.neurosymbolic.similarity import get_similarity_engine

_engine = get_similarity_engine()


def cosine_similarity(a, b):
    """Backward-compatible cosine; prefer attention via score_prototypes."""
    a = np.array(a, dtype=np.float64)
    b = np.array(b, dtype=np.float64)
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom < 1e-9:
        return 0.0
    return float(np.dot(a, b) / denom)


def score_prototypes(query_vec, prototypes: list) -> float:
    return _engine.score(query_vec, prototypes)


def mean_embedding(embeddings):
    return np.mean(embeddings, axis=0).tolist()


__all__ = ["get_embedding", "cosine_similarity", "score_prototypes", "mean_embedding"]
