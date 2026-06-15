"""Prototype attention similarity — replaces centroid cosine matching."""

import numpy as np

from app.core.config import ATTENTION_TEMPERATURE


def _normalize(vec) -> np.ndarray:
    v = np.array(vec, dtype=np.float64)
    norm = np.linalg.norm(v)
    if norm < 1e-9:
        return v
    return v / norm


def _softmax(x: np.ndarray) -> np.ndarray:
    x = x - np.max(x)
    exp = np.exp(x)
    return exp / (exp.sum() + 1e-9)


class PrototypeAttentionSimilarity:
    def __init__(self, temperature: float = ATTENTION_TEMPERATURE):
        self.temperature = temperature

    def score(self, query_vec, prototypes: list) -> float:
        if not prototypes:
            return 0.0
        q = _normalize(query_vec)
        keys = np.stack([_normalize(p) for p in prototypes])
        logits = (keys @ q) / self.temperature
        weights = _softmax(logits)
        similarities = keys @ q
        return float(np.clip(np.sum(weights * similarities), 0.0, 1.0))

    def score_with_weights(
        self, query_vec, prototypes: list
    ) -> tuple:
        if not prototypes:
            return 0.0, []
        q = _normalize(query_vec)
        keys = np.stack([_normalize(p) for p in prototypes])
        logits = (keys @ q) / self.temperature
        weights = _softmax(logits)
        similarities = keys @ q
        score = float(np.clip(np.sum(weights * similarities), 0.0, 1.0))
        return score, weights.tolist()

    def rank(
        self, query_vec, category_prototypes: dict
    ) -> list:
        scores = [
            (cat, round(self.score(query_vec, protos), 4))
            for cat, protos in category_prototypes.items()
            if protos
        ]
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores
