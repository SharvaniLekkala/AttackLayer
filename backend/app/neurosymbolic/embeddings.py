"""Embedding service wrapper."""

from app.memory.embedding_service import generate_embedding


def get_embedding(text: str) -> list:
    return generate_embedding(text)
