"""
V2 Explainability Engine — structured reasons for every security decision.
"""


def build_explanation(
    intent_result=None,
    security_result=None,
    memory_verification=None,
    retrieval_result=None,
    response_validation=None,
    final_decision="ALLOW",
):
    reasons = []

    if intent_result:
        reasons.append({
            "component": "intent_classifier",
            "decision": intent_result.get("intent", "UNKNOWN"),
            "confidence": intent_result.get("confidence", 0.0),
            "reason": (
                f"Classified as {intent_result.get('intent')} "
                f"with {intent_result.get('confidence', 0):.0%} confidence"
            ),
        })

    if security_result:
        attack = security_result.get("attack_type", "SAFE")
        if attack != "SAFE":
            reasons.append({
                "component": "security_classifier",
                "decision": attack,
                "confidence": security_result.get("confidence", 0.0),
                "reason": (
                    f"Detected {attack} attack "
                    f"(risk: {security_result.get('risk_level', 'LOW')}, "
                    f"confidence: {security_result.get('confidence', 0):.0%})"
                ),
            })
        else:
            reasons.append({
                "component": "security_classifier",
                "decision": "SAFE",
                "confidence": security_result.get("confidence", 0.0),
                "reason": "No attack patterns detected in input",
            })

    if memory_verification:
        status = memory_verification.get("verification_status")
        if status == "blocked":
            reasons.append({
                "component": "memory_verification",
                "decision": "BLOCK",
                "confidence": memory_verification.get("confidence", 0.0),
                "reason": "Memory rejected: security policy violation",
            })
        elif status == "quarantined":
            detail = []
            if memory_verification.get("has_conflict"):
                detail.append("conflicts with existing memory")
            if memory_verification.get("is_suspicious"):
                detail.append("suspicious content detected")
            reasons.append({
                "component": "memory_verification",
                "decision": "QUARANTINE",
                "confidence": memory_verification.get("confidence", 0.0),
                "reason": (
                    "Memory quarantined: "
                    + (", ".join(detail) if detail else "requires review")
                ),
            })
        elif status == "conflict_review":
            reasons.append({
                "component": "memory_verification",
                "decision": "CONFLICT",
                "confidence": memory_verification.get("confidence", 0.0),
                "reason": "Potential conflict with existing memory detected",
            })

    if retrieval_result:
        blocked = retrieval_result.get("blocked_count", 0)
        safe = len(retrieval_result.get("safe_memories", []))
        if blocked > 0:
            reasons.append({
                "component": "memory_retrieval",
                "decision": "FILTERED",
                "confidence": retrieval_result.get("retrieval_confidence", 0.8),
                "reason": (
                    f"Retrieved {safe} safe memories, "
                    f"blocked {blocked} low-trust memories"
                ),
            })
        else:
            reasons.append({
                "component": "memory_retrieval",
                "decision": "RETRIEVED",
                "confidence": retrieval_result.get("retrieval_confidence", 0.8),
                "reason": f"Retrieved {safe} relevant memories",
            })

    if response_validation:
        if response_validation.get("regenerated"):
            reasons.append({
                "component": "response_validator",
                "decision": "REGENERATED",
                "confidence": response_validation.get("response_confidence", 0.5),
                "reason": "Response regenerated due to low confidence",
            })
        issues = response_validation.get("issues", [])
        for issue in issues:
            reasons.append({
                "component": "response_validator",
                "decision": "WARNING",
                "confidence": response_validation.get("security_confidence", 0.8),
                "reason": issue,
            })

    summary = _build_summary(reasons, final_decision)

    return {
        "reasons": reasons,
        "summary": summary,
        "final_decision": final_decision,
    }


def _build_summary(reasons, final_decision):
    if final_decision == "BLOCK":
        block_reasons = [
            r["reason"]
            for r in reasons
            if r["decision"] in ("BLOCK", "QUARANTINE", "PROMPT_INJECTION", "MEMORY_POISONING")
        ]
        if block_reasons:
            return block_reasons[0]
        return "Request blocked by security policy"

    attack_reasons = [
        r for r in reasons
        if r.get("component") == "security_classifier"
        and r.get("decision") != "SAFE"
    ]
    if attack_reasons:
        return attack_reasons[0]["reason"]

    return "Request processed normally"
