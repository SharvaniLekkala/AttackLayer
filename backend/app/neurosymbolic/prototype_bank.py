"""
Scalable prototype bank — lazy-loaded embeddings from local corpus + HF-ready loader.
"""

from app.neurosymbolic.embeddings import get_embedding
from app.data.local_corpus import (
    CATEGORY_EXAMPLES,
    MEMORY_TYPE_EXAMPLES,
    ATTACK_EXAMPLES,
    STORE_EXAMPLES,
    IGNORE_EXAMPLES,
    QUERY_CATEGORY_EXAMPLES,
    INTENT_EXAMPLES,
)

_embedding_cache: dict = {}
_prototype_cache: dict = {}


def _embed_texts(texts: list) -> list:
    return [get_embedding(t) for t in texts]


def get_category_prototypes() -> dict:
    if "category" not in _prototype_cache:
        _prototype_cache["category"] = {
            cat: _embed_texts(examples)
            for cat, examples in CATEGORY_EXAMPLES.items()
        }
    return _prototype_cache["category"]


def get_memory_type_prototypes() -> dict:
    if "memory_type" not in _prototype_cache:
        _prototype_cache["memory_type"] = {
            mtype: _embed_texts(examples)
            for mtype, examples in MEMORY_TYPE_EXAMPLES.items()
        }
    return _prototype_cache["memory_type"]


def get_attack_prototypes() -> dict:
    if "attack" not in _prototype_cache:
        _prototype_cache["attack"] = {
            attack: _embed_texts(examples)
            for attack, examples in ATTACK_EXAMPLES.items()
        }
    return _prototype_cache["attack"]


def get_worthiness_prototypes() -> dict:
    if "worthiness" not in _prototype_cache:
        _prototype_cache["worthiness"] = {
            "STORE": _embed_texts(STORE_EXAMPLES),
            "IGNORE": _embed_texts(IGNORE_EXAMPLES),
        }
    return _prototype_cache["worthiness"]


def get_query_category_prototypes() -> dict:
    if "query_category" not in _prototype_cache:
        _prototype_cache["query_category"] = {
            cat: _embed_texts(examples)
            for cat, examples in QUERY_CATEGORY_EXAMPLES.items()
        }
    return _prototype_cache["query_category"]


def get_intent_prototypes() -> dict:
    if "intent" not in _prototype_cache:
        _prototype_cache["intent"] = {
            intent: _embed_texts(examples)
            for intent, examples in INTENT_EXAMPLES.items()
        }
    return _prototype_cache["intent"]


def clear_cache():
    _prototype_cache.clear()
    _embedding_cache.clear()


def merge_hf_examples(category: str, examples: list):
    """Extend prototype bank with HuggingFace dataset examples."""
    if category not in CATEGORY_EXAMPLES:
        CATEGORY_EXAMPLES[category] = []
    CATEGORY_EXAMPLES[category].extend(examples)
    if "category" in _prototype_cache:
        del _prototype_cache["category"]
