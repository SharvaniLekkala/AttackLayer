import chromadb


client = chromadb.PersistentClient(
    path="./chroma_db"
)

memory_collection = client.get_or_create_collection(
    name="memory_vault"
)
def add_memory_embedding(
    memory_id: int,
    text: str,
    embedding
):

    memory_collection.add(
        ids=[str(memory_id)],
        documents=[text],
        embeddings=[embedding]
    )
def semantic_search(
    embedding,
    top_k=5
):

    results = memory_collection.query(
        query_embeddings=[embedding],
        n_results=top_k
    )

    return results