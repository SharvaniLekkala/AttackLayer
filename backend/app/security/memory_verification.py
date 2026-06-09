"""
V2 Memory Verification — pre-store conflict and suspicion checks.
"""

from app.security.memory_conflict_engine import detect_conflict
from app.security.security_classifier import classify_security
from app.security.semantic_classifier import classify_memory


def verify_memory(db, user_id, fact):
    security = classify_security(fact)
    category = classify_memory(fact)["category"]
    conflict = detect_conflict(db, user_id, fact, category)

    is_suspicious = security["attack_type"] != "SAFE"
    has_conflict = conflict is not None and conflict.get("conflict_score", 0) >= 0.6

    if security["decision"] == "BLOCK":
        status = "blocked"
        confidence = security["confidence"]
    elif has_conflict and conflict.get("conflict_score", 0) >= 0.7:
        status = "quarantined"
        confidence = conflict.get("conflict_score", 0.7)
    elif is_suspicious and security["confidence"] >= 0.65:
        status = "quarantined"
        confidence = security["confidence"]
    elif has_conflict:
        status = "conflict_review"
        confidence = conflict.get("conflict_score", 0.5)
    else:
        status = "approved"
        confidence = 0.9

    trust_delta = 0.0
    if has_conflict:
        trust_delta = -0.15
    if is_suspicious:
        trust_delta = min(trust_delta, -0.2)

    return {
        "verification_status": status,
        "confidence": round(confidence, 4),
        "has_conflict": has_conflict,
        "is_suspicious": is_suspicious,
        "conflict_details": conflict,
        "security_details": security,
        "trust_delta": trust_delta,
        "should_quarantine": status in ("quarantined", "blocked"),
        "preserve_old_memory": has_conflict,
    }
