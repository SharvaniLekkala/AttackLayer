"""Embedding service wrapper."""

from app.memory.embedding_service import generate_embedding

_cache = {}

def get_embedding(text: str) -> list:
    if text not in _cache:
        _cache[text] = generate_embedding(text)
    return _cache[text]

