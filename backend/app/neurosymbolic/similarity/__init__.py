from app.core.config import SIMILARITY_ENGINE
from app.neurosymbolic.similarity.attention import PrototypeAttentionSimilarity
from app.neurosymbolic.similarity.cosine import CosineSimilarityEngine

_engine = None


def get_similarity_engine():
    global _engine
    if _engine is None:
        if SIMILARITY_ENGINE == "cosine":
            _engine = CosineSimilarityEngine()
        else:
            _engine = PrototypeAttentionSimilarity()
    return _engine
