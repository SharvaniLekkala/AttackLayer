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
    print(
    "ATTACKLAYER_HF_DATASETS =",
    os.getenv("ATTACKLAYER_HF_DATASETS")
)
    """
    Load memory poisoning attack dataset from HuggingFace.

    Returns:

    {
        "PROMPT_INJECTION": [
            "...",
            "...",
        ],
        "ROLE_HIJACK": [
            "...",
        ]
    }
    """

    if os.getenv("ATTACKLAYER_HF_DATASETS", "0") != "1":
        return load_local_poisoning_corpus()

    try:
        import pandas as pd
        print("LOADING HF DATASET...")
        df = pd.read_json(
            "hf://datasets/vgudur/memory-poisoning-attack-corpus/data/train.jsonl",
            lines=True,
        )
        
        print(df.shape)
        print(df.head())
        CATEGORY_MAP = {
            "benign": "SAFE",
            "instruction_override": "PROMPT_INJECTION",
            "prompt_injection": "PROMPT_INJECTION",
            "secret_leakage": "SYSTEM_PROMPT_EXTRACTION",
            "role_hijacking": "ROLE_HIJACK",
            "data_exfiltration": "MEMORY_POISONING",
            "integrity_tampering": "FALSE_FACT_INJECTION",
        }

        corpus = {}

        for _, row in df.iterrows():

            category = CATEGORY_MAP.get(
                row["category"],
                row["category"].upper(),
            )

            text = str(row["text"]).strip()

            if not text:
                continue

            corpus.setdefault(category, [])

            if text not in corpus[category]:
                corpus[category].append(text)

        return corpus

    except Exception as e:
        print("HF DATASET LOAD FAILED:", e)
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
if __name__ == "__main__":

    corpus = load_hf_poisoning_corpus()

    print("--------------------------------")
    print("Loaded Categories")
    print("--------------------------------")

    for k, v in corpus.items():
        print(k, len(v))

    print("--------------------------------")