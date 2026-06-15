"""Pluggable similarity engine protocol."""

from typing import Protocol, List, Tuple, Dict, Any


class SimilarityEngine(Protocol):
    def score(self, query_vec, prototypes: list) -> float:
        ...

    def rank(
        self, query_vec, category_prototypes: Dict[str, list]
    ) -> List[Tuple[str, float]]:
        ...

    def score_with_weights(
        self, query_vec, prototypes: list
    ) -> Tuple[float, List[float]]:
        ...
