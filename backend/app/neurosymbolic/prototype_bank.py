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
from app.data.dataset_loader import load_hf_poisoning_corpus
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

        merged_examples = {}

        # Existing local corpus
        for attack, examples in ATTACK_EXAMPLES.items():
            merged_examples[attack] = list(examples)

        # HF dataset
        hf_examples = load_hf_poisoning_corpus()

        HF_TO_ATTACKLAYER = {
    "PROMPT_INJECTION": "PROMPT_INJECTION",
    "SYSTEM_PROMPT_EXTRACTION": "SYSTEM_PROMPT_EXTRACTION",
    "ROLE_HIJACK": "ROLE_HIJACK",
    "MEMORY_POISONING": "MEMORY_POISONING",
    "FALSE_FACT_INJECTION": "FALSE_FACT_INJECTION",
    "SAFE": None,
}

        for hf_category, texts in hf_examples.items():

            mapped_attack = HF_TO_ATTACKLAYER.get(hf_category)

            if not mapped_attack:
                continue

            merged_examples.setdefault(mapped_attack, [])

            existing = set(merged_examples[mapped_attack])

            for text in texts:

                if text not in existing:
                    merged_examples[mapped_attack].append(text)

        print("\n=== ATTACK PROTOTYPE COUNTS ===")

        for attack, examples in merged_examples.items():
            print(f"{attack}: {len(examples)}")

        print("===============================\n")

        _prototype_cache["attack"] = {
            attack: _embed_texts(examples)
            for attack, examples in merged_examples.items()
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
