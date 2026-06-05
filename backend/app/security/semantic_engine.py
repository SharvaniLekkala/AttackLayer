import numpy as np

from app.memory.embedding_service import (
    generate_embedding
)


def cosine_similarity(a, b):

    a = np.array(a)
    b = np.array(b)

    return float(
        np.dot(a, b)
        /
        (
            np.linalg.norm(a)
            * np.linalg.norm(b)
        )
    )


def get_embedding(text: str):

    return generate_embedding(text)


def mean_embedding(embeddings):

    return np.mean(
        embeddings,
        axis=0
    ).tolist()