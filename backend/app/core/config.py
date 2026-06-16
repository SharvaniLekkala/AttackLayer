"""Central configuration for AttackLayer."""

import os
from dotenv import load_dotenv

load_dotenv()


OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2")

# attention | cosine
SIMILARITY_ENGINE = os.getenv("SIMILARITY_ENGINE", "attention")
ATTENTION_TEMPERATURE = float(os.getenv("ATTENTION_TEMPERATURE", "0.07"))

TRUST_WEIGHTS = {
    "neural": float(os.getenv("TRUST_WEIGHT_NEURAL", "0.35")),
    "rules": float(os.getenv("TRUST_WEIGHT_RULES", "0.25")),
    "historical": float(os.getenv("TRUST_WEIGHT_HISTORICAL", "0.20")),
    "verification": float(os.getenv("TRUST_WEIGHT_VERIFICATION", "0.20")),
}

CLASSIFICATION_CONFIDENCE_THRESHOLD = float(
    os.getenv("CLASSIFICATION_CONFIDENCE_THRESHOLD", "0.52")
)

ATTACK_BLOCK_THRESHOLD = float(os.getenv("ATTACK_BLOCK_THRESHOLD", "0.68"))
ATTACK_HITL_THRESHOLD = float(os.getenv("ATTACK_HITL_THRESHOLD", "0.58"))
