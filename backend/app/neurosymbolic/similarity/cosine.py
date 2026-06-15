"""Cosine similarity fallback engine."""

import numpy as np


def _normalize(vec) -> np.ndarray:
    v = np.array(vec, dtype=np.float64)
    norm = np.linalg.norm(v)
    if norm < 1e-9:
        return v
    return v / norm


def _cosine(a, b) -> float:
    return float(np.clip(_normalize(a) @ _normalize(b), 0.0, 1.0))


def _mean(prototypes: list) -> list:
    return np.mean(
        [_normalize(p) for p in prototypes], axis=0
    ).tolist()


class CosineSimilarityEngine:
    def score(self, query_vec, prototypes: list) -> float:
        if not prototypes:
            return 0.0
        centroid = _mean(prototypes)
        return _cosine(query_vec, centroid)

    def score_with_weights(self, query_vec, prototypes: list) -> tuple:
        score = self.score(query_vec, prototypes)
        n = len(prototypes)
        weights = [1.0 / n] * n if n else []
        return score, weights

    def rank(self, query_vec, category_prototypes: dict) -> list:
        scores = [
            (cat, round(self.score(query_vec, protos), 4))
            for cat, protos in category_prototypes.items()
            if protos
        ]
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores
