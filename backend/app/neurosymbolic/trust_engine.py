"""
NeuroSymbolic Trust Engine — explainable composite trust scoring.
"""

from datetime import datetime, timezone

from app.core.config import TRUST_WEIGHTS


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def compute_neural_score(
    semantic_confidence: float,
    poison_confidence: float,
    contradiction_confidence: float,
    embedding_confidence: float = None,
) -> dict:
    emb_conf = embedding_confidence if embedding_confidence is not None else semantic_confidence
    poison_penalty = poison_confidence * 0.5
    contradiction_penalty = contradiction_confidence * 0.3
    score = (
        0.35 * emb_conf
        + 0.35 * semantic_confidence
        + 0.20 * (1.0 - poison_penalty)
        + 0.10 * (1.0 - contradiction_penalty)
    )
    return {
        "score": round(_clamp(score), 4),
        "semantic_confidence": round(semantic_confidence, 4),
        "poison_confidence": round(poison_confidence, 4),
        "contradiction_confidence": round(contradiction_confidence, 4),
        "embedding_confidence": round(emb_conf, 4),
    }


def compute_rule_score(
    security_decision: str,
    category: str,
    attack_type: str,
    memory_age_days: float = 0,
    version: int = 1,
) -> dict:
    score = 1.0
    triggered = []

    benign_categories = {
        "FOOD_PREFERENCE", "CODING_PREFERENCE", "PROFESSION", "LOCATION",
        "PERSONAL_INFO", "CAREER", "STUDY_DOMAIN", "GENERAL_FACT", "GENERAL",
    }
    if category in benign_categories and attack_type in ("SAFE", "NONE"):
        triggered.append("benign_category")
        score = max(score, 0.85)

    if security_decision == "BLOCK":
        score -= 0.40
        triggered.append("security_block")

    if version > 1:
        penalty = min(0.15, (version - 1) * 0.03)
        score -= penalty
        triggered.append("version_history")

    if memory_age_days > 30:
        score += 0.05
        triggered.append("established_memory")

    return {"score": round(_clamp(score), 4), "triggered": triggered}


def compute_historical_score(
    conflict_count: int = 0,
    attack_history: str = "",
    hitl_rejected: bool = False,
    propagation_exposed: bool = False,
) -> dict:
    score = 1.0
    if conflict_count > 0:
        score -= min(0.30, conflict_count * 0.08)
    if attack_history:
        score -= 0.20
    if hitl_rejected:
        score -= 0.35
    if propagation_exposed:
        score -= 0.25
    return {
        "score": round(_clamp(score), 4),
        "conflict_count": conflict_count,
        "attack_history": attack_history or "",
    }


def compute_verification_score(
    verification_count: int = 0,
    source: str = "USER",
    verified: bool = False,
    hitl_approved: bool = False,
) -> dict:
    source_trust = {
        "HITL_APPROVED": 0.95,
        "SYSTEM": 0.80,
        "USER": 0.65,
    }.get(source, 0.60)

    score = source_trust
    if verified:
        score += 0.10
    if hitl_approved:
        score += 0.15
    score += min(0.15, verification_count * 0.05)

    return {
        "score": round(_clamp(score), 4),
        "verification_count": verification_count,
        "source": source,
    }


def calculate_trust(
    source="USER",
    security_decision="ALLOW",
    category_confidence=0.5,
    conflict_detected=False,
    version=1,
    attack_type=None,
    poison_score=0.0,
    conflict_score=0.0,
    category="GENERAL",
    verification_count=0,
    verified=False,
    conflict_count=0,
    attack_history="",
    hitl_approved=False,
    hitl_rejected=False,
    memory_created_at=None,
    propagation_exposed=False,
):
    poison_confidence = poison_score if poison_score else (
        0.90 if attack_type == "MEMORY_POISONING" else
        0.70 if attack_type == "PROMPT_INJECTION" else
        0.85 if attack_type == "TOOL_POLICY_MANIPULATION" else
        0.88 if attack_type == "PROPAGATION_ATTACK" else 0.0
    )
    contradiction_confidence = conflict_score if conflict_score else (0.60 if conflict_detected else 0.0)

    age_days = 0.0
    if memory_created_at:
        now = datetime.now(timezone.utc)
        created = memory_created_at
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        age_days = (now - created).total_seconds() / 86400

    neural = compute_neural_score(
        semantic_confidence=category_confidence,
        poison_confidence=poison_confidence,
        contradiction_confidence=contradiction_confidence,
    )
    rules = compute_rule_score(
        security_decision=security_decision,
        category=category,
        attack_type=attack_type or "NONE",
        memory_age_days=age_days,
        version=version,
    )
    historical = compute_historical_score(
        conflict_count=conflict_count,
        attack_history=attack_history,
        hitl_rejected=hitl_rejected,
        propagation_exposed=propagation_exposed,
    )
    verification = compute_verification_score(
        verification_count=verification_count,
        source="HITL_APPROVED" if hitl_approved else source,
        verified=verified,
        hitl_approved=hitl_approved,
    )

    w = TRUST_WEIGHTS
    final = (
        w["neural"] * neural["score"]
        + w["rules"] * rules["score"]
        + w["historical"] * historical["score"]
        + w["verification"] * verification["score"]
    )
    final = round(_clamp(final), 4)

    explanation_parts = []
    if neural["score"] >= 0.7:
        explanation_parts.append("Strong semantic match")
    if poison_confidence > 0.5:
        explanation_parts.append(f"Poisoning signal detected ({poison_confidence:.2f})")
    if rules["triggered"]:
        explanation_parts.append(f"Rules: {', '.join(rules['triggered'])}")
    if hitl_approved:
        explanation_parts.append("Human approved")
    if conflict_detected:
        explanation_parts.append("Conflict with existing memory")

    return {
        "trust_score": final,
        "confidence_score": category_confidence,
        "conflict_score": round(contradiction_confidence, 4),
        "poison_score": round(poison_confidence, 4),
        "trust_explanation": {
            "summary": "; ".join(explanation_parts) or "Default trust assessment",
            "components": {
                "neural": neural,
                "rules": rules,
                "historical": historical,
                "verification": verification,
            },
            "weights": w,
            "final_trust_score": final,
        },
    }
