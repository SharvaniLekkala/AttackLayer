"""
Unified attack registry — 7 attack classes with detection, risk, mitigation.
Uses prototype attention + symbolic rules (NeuroSymbolic).
"""

import re

from app.core.config import ATTACK_BLOCK_THRESHOLD, ATTACK_HITL_THRESHOLD
from app.core.types import BENIGN_CATEGORIES
from app.data.local_corpus import ATTACK_TYPE_TO_MITIGATION, CATEGORY_TO_ATTACK_TYPE
from app.neurosymbolic.embeddings import get_embedding
from app.neurosymbolic.prototype_bank import get_attack_prototypes
from app.neurosymbolic.similarity import get_similarity_engine
from app.security.sensitive_detector import detect_sensitive_data

_engine = get_similarity_engine()

BLOCK_PATTERNS = [
    (r"ignore\s+(all\s+)?previous\s+instructions", "PROMPT_INJECTION"),
    (r"forget\s+(all\s+)?(prior|previous)\s+rules", "PROMPT_INJECTION"),
    (r"disregard\s+prior\s+instructions", "PROMPT_INJECTION"),
    (r"bypass\s+(your\s+)?safety", "PROMPT_INJECTION"),
    (r"remember\s+that\s+2\s*\+\s*2\s*=\s*5", "FALSE_FACT_INJECTION"),
    (r"store\s+that\s+2\s*\+\s*2\s*=\s*5", "FALSE_FACT_INJECTION"),
    (r"2\s*\+\s*2\s*=\s*5", "FALSE_FACT_INJECTION"),
    (r"overwrite\s+all\s+previous\s+memories", "MEMORY_OVERWRITE"),
    (r"replace\s+every\s+stored\s+fact", "MEMORY_OVERWRITE"),
    (r"reveal\s+your\s+system\s+prompt", "SYSTEM_PROMPT_EXTRACTION"),
    (r"show\s+me\s+your\s+hidden\s+instructions", "SYSTEM_PROMPT_EXTRACTION"),
]

HITL_PATTERNS = [
    (r"trust\s+all\s+external\s+apis?", "TOOL_POLICY_MANIPULATION"),
    (r"disable\s+tool\s+validation", "TOOL_POLICY_MANIPULATION"),
    (r"allow\s+all\s+tools", "TOOL_POLICY_MANIPULATION"),
]

RISK_LEVELS = {
    "SAFE": "LOW",
    "PROMPT_INJECTION": "CRITICAL",
    "MEMORY_POISONING": "CRITICAL",
    "FALSE_FACT_INJECTION": "CRITICAL",
    "PREFERENCE_MANIPULATION": "HIGH",
    "TOOL_POLICY_MANIPULATION": "HIGH",
    "MEMORY_OVERWRITE": "HIGH",
    "PROPAGATION_ATTACK": "CRITICAL",
    "SYSTEM_PROMPT_EXTRACTION": "HIGH",
    "ROLE_HIJACK": "HIGH",
    "SOCIAL_ENGINEERING": "MEDIUM",
    "SUSPICIOUS": "MEDIUM",
}

SEVEN_ATTACKS = [
    "MEMORY_POISONING",
    "PROMPT_INJECTION",
    "FALSE_FACT_INJECTION",
    "PREFERENCE_MANIPULATION",
    "TOOL_POLICY_MANIPULATION",
    "MEMORY_OVERWRITE",
    "PROPAGATION_ATTACK",
]


def _check_patterns(text: str, patterns: list) -> tuple:
    lowered = text.lower()
    for pattern, attack_type in patterns:
        if re.search(pattern, lowered):
            return attack_type, 0.98
    return None, 0.0


def _apply_benign_override(text: str, category: str, attack_type: str, confidence: float):
    """Symbolic rule: declarative benign statements must not be flagged as attacks."""
    lowered = text.lower()
    manipulation_signals = (
        "hate ", "forever", "wrong", "insecure", "strangers", "bypass",
        "change my preference", "from now on", "always trust", "publicly",
        "maximum risk", "only java forever",
    )
    attack_phrases = (
        "ignore", "bypass", "override", "forget all", "reveal",
        "trust all external", "2+2=5", "2 + 2 = 5",
    )

    if category in BENIGN_CATEGORIES:
        if any(p in lowered for p in attack_phrases):
            return attack_type, confidence, None
        if attack_type == "PREFERENCE_MANIPULATION" and not any(
            s in lowered for s in manipulation_signals
        ):
            return "SAFE", 0.05, "ALLOW"
        if attack_type in ("SAFE", "NONE", "SUSPICIOUS", "SOCIAL_ENGINEERING"):
            return "SAFE", 0.05, "ALLOW"
    return attack_type, confidence, None


def classify_security(text: str, category: str = None) -> dict:
    embedding = get_embedding(text)
    prototypes = get_attack_prototypes()
    scores = _engine.rank(embedding, prototypes)

    attack_type = "SAFE"
    confidence = 0.0
    alternatives = []

    if scores:
        attack_type, confidence = scores[0]
        alternatives = [{"attack_type": a, "confidence": s} for a, s in scores[1:5]]

    pattern_attack, pattern_conf = _check_patterns(text, BLOCK_PATTERNS)
    if pattern_conf > confidence:
        attack_type = pattern_attack
        confidence = pattern_conf

    hitl_attack, hitl_conf = _check_patterns(text, HITL_PATTERNS)
    forced_decision = None
    if hitl_conf > confidence:
        attack_type = hitl_attack
        confidence = hitl_conf
        forced_decision = "ALLOW_WITH_WARNING"

    sensitive = detect_sensitive_data(text)
    if sensitive["decision"] == "BLOCK":
        attack_type = "MEMORY_POISONING"
        confidence = max(confidence, 0.95)
        forced_decision = "BLOCK"

    if category:
        attack_type, confidence, benign_decision = _apply_benign_override(
            text, category, attack_type, confidence
        )
        if benign_decision:
            forced_decision = benign_decision

    if attack_type == "SAFE" or confidence < 0.55:
        attack_type = "SAFE"
        confidence = round(1.0 - confidence, 4) if confidence > 0 else 0.95
        decision = "ALLOW"
    elif forced_decision:
        decision = forced_decision
    elif attack_type in ("PROMPT_INJECTION", "FALSE_FACT_INJECTION", "MEMORY_POISONING",
                         "MEMORY_OVERWRITE", "PROPAGATION_ATTACK", "SYSTEM_PROMPT_EXTRACTION",
                         "ROLE_HIJACK") and confidence >= ATTACK_BLOCK_THRESHOLD:
        decision = "BLOCK"
    elif attack_type == "TOOL_POLICY_MANIPULATION" and confidence >= ATTACK_HITL_THRESHOLD:
        decision = "ALLOW_WITH_WARNING"
    elif confidence >= ATTACK_BLOCK_THRESHOLD:
        decision = "BLOCK"
    elif confidence >= ATTACK_HITL_THRESHOLD:
        decision = "ALLOW_WITH_WARNING"
    else:
        decision = "ALLOW"

    mitigation = ATTACK_TYPE_TO_MITIGATION.get(attack_type, "NONE")

    return {
        "attack_type": attack_type,
        "risk_score": round(confidence if attack_type != "SAFE" else 0.0, 4),
        "risk_level": RISK_LEVELS.get(attack_type, "LOW"),
        "confidence": round(confidence, 4),
        "decision": decision,
        "mitigation": mitigation,
        "alternatives": alternatives,
        "dataset_categories": list(CATEGORY_TO_ATTACK_TYPE.keys()),
        "seven_attacks": SEVEN_ATTACKS,
    }


def assess_all_attacks(text: str) -> list:
    """Return per-attack detection results for dashboard/benchmarking."""
    embedding = get_embedding(text)
    prototypes = get_attack_prototypes()
    results = []
    for attack in SEVEN_ATTACKS:
        protos = prototypes.get(attack, [])
        score = _engine.score(embedding, protos) if protos else 0.0
        detected = score >= ATTACK_HITL_THRESHOLD
        results.append({
            "attack_type": attack,
            "detected": detected,
            "risk_score": round(score, 4),
            "mitigation": ATTACK_TYPE_TO_MITIGATION.get(attack, "NONE"),
        })
    return results
