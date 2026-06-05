from app.memory.embedding_service import (
    generate_embedding
)

from app.memory.vector_storage import (
    semantic_search
)
@router.get("/search")
def search_memory(
    query: str
):

    embedding = generate_embedding(query)

    results = semantic_search(
        embedding
    )

    return results