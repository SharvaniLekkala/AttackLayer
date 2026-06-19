import ollama


EMBED_MODEL = "nomic-embed-text"

_cache = {}

def generate_embedding(text: str):
    if text not in _cache:
        response = ollama.embeddings(
            model=EMBED_MODEL,
            prompt=text
        )
        _cache[text] = response["embedding"]
    return _cache[text]