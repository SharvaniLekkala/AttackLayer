"""
HuggingFace dataset loader — extends prototype bank at runtime.
Reference: vgudur/memory-poisoning-attack-corpus
"""

import json
import os

from app.data.local_corpus import CATEGORY_EXAMPLES, ATTACK_EXAMPLES
from app.research.poisoning_dataset import POISONING_DATASET


def load_local_poisoning_corpus() -> dict:
    """Local fallback — mirrors HF memory-poisoning-attack-corpus structure."""
    return POISONING_DATASET.copy()


def load_hf_poisoning_corpus(cache_dir: str = None) -> dict:
    """
    Load from HuggingFace when available; fall back to local corpus.
    Set ATTACKLAYER_HF_DATASETS=1 to attempt network load.
    """
    if os.getenv("ATTACKLAYER_HF_DATASETS", "0") != "1":
        return load_local_poisoning_corpus()

    try:
        from datasets import load_dataset

        ds = load_dataset(
            "vgudur/memory-poisoning-attack-corpus",
            split="train",
            cache_dir=cache_dir,
        )
        corpus = {}
        for row in ds:
            category = row.get("category") or row.get("attack_type") or "UNKNOWN"
            text = row.get("text") or row.get("prompt") or row.get("example", "")
            if not text:
                continue
            corpus.setdefault(category, []).append(text)
        return corpus if corpus else load_local_poisoning_corpus()
    except Exception:
        return load_local_poisoning_corpus()


def load_hf_memory_datasets() -> dict:
    """Search-based memory dataset loader — extends category examples."""
    if os.getenv("ATTACKLAYER_HF_DATASETS", "0") != "1":
        return {}

    extended = {}
    try:
        from datasets import load_dataset

        for name in ("memorybank/MemoryBank",):
            try:
                ds = load_dataset(name, split="train")
                for row in ds:
                    text = row.get("text") or row.get("content") or ""
                    cat = row.get("category", "GENERAL")
                    if text:
                        extended.setdefault(cat, []).append(text)
            except Exception:
                continue
    except Exception:
        pass
    return extended


def bootstrap_prototypes():
    """Merge HF corpus into local prototype definitions."""
    hf_corpus = load_hf_poisoning_corpus()
    attack_map = {
        "FALSE_FACT_INJECTION": "FALSE_FACT_INJECTION",
        "PREFERENCE_MANIPULATION": "PREFERENCE_MANIPULATION",
        "ROLE_HIJACKING": "ROLE_HIJACK",
        "PROMPT_INJECTION": "PROMPT_INJECTION",
        "DELAYED_POISONING": "MEMORY_POISONING",
        "MEMORY_OVERRIDE": "MEMORY_OVERWRITE",
        "TOOL_MANIPULATION": "TOOL_POLICY_MANIPULATION",
        "SYSTEM_PROMPT_EXTRACTION": "SYSTEM_PROMPT_EXTRACTION",
    }
    for hf_cat, examples in hf_corpus.items():
        attack_key = attack_map.get(hf_cat, hf_cat)
        if attack_key in ATTACK_EXAMPLES:
            existing = set(ATTACK_EXAMPLES[attack_key])
            for ex in examples:
                if ex not in existing:
                    ATTACK_EXAMPLES[attack_key].append(ex)

    hf_memory = load_hf_memory_datasets()
    for cat, examples in hf_memory.items():
        normalized = cat.upper().replace(" ", "_")
        if normalized in CATEGORY_EXAMPLES:
            existing = set(CATEGORY_EXAMPLES[normalized])
            for ex in examples:
                if ex not in existing:
                    CATEGORY_EXAMPLES[normalized].append(ex)


def export_benchmark_json(path: str, metrics: dict):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
