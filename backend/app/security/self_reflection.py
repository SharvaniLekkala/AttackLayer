"""
V2 Self Reflection — internal post-response analysis (not shown to user).
"""

from app.database.models import ReflectionLog


def generate_reflection(
    query,
    response,
    intent_result,
    security_result,
    retrieval_result,
    response_validation,
    memories_used,
):
    issues = []
    improvements = []

    supported = True
    if retrieval_result and not retrieval_result.get("safe_memories"):
        if intent_result.get("intent") == "QUESTION":
            issues.append("retrieval_returned_no_memories_for_question")
            supported = False

    low_trust_used = False
    for mem in memories_used or []:
        if isinstance(mem, dict) and mem.get("trust_score", 1.0) < 0.5:
            low_trust_used = True
            issues.append("used_low_trust_memory")

    if security_result.get("attack_type") != "SAFE":
        if security_result.get("decision") == "ALLOW":
            issues.append("potential_attack_bypass")
            improvements.append("tighten_security_threshold")

    if response_validation:
        if response_validation.get("response_confidence", 1.0) < 0.6:
            improvements.append("improve_context_quality")
        if response_validation.get("issues"):
            improvements.append("strengthen_response_validation")

    report = {
        "query": query[:200],
        "answer_supported": supported,
        "retrieval_success": bool(
            retrieval_result and retrieval_result.get("safe_memories")
        ),
        "low_trust_memory_used": low_trust_used,
        "attack_bypass_suspected": "potential_attack_bypass" in issues,
        "issues": issues,
        "improvements": improvements,
        "confidence_scores": {
            "response": response_validation.get("response_confidence", 0.8)
            if response_validation else 0.8,
            "memory": response_validation.get("memory_confidence", 0.8)
            if response_validation else 0.8,
            "security": response_validation.get("security_confidence", 0.9)
            if response_validation else 0.9,
        },
    }

    return report


def store_reflection(db, report):
    entry = ReflectionLog(
        query=report.get("query", ""),
        answer_supported=report.get("answer_supported", True),
        retrieval_success=report.get("retrieval_success", False),
        low_trust_memory_used=report.get("low_trust_memory_used", False),
        attack_bypass_suspected=report.get("attack_bypass_suspected", False),
        issues=",".join(report.get("issues", [])),
        improvements=",".join(report.get("improvements", [])),
        response_confidence=report.get("confidence_scores", {}).get("response", 0.0),
        memory_confidence=report.get("confidence_scores", {}).get("memory", 0.0),
        security_confidence=report.get("confidence_scores", {}).get("security", 0.0),
    )
    db.add(entry)
    db.commit()
    return entry
