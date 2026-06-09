from app.security.intent_classifier import classify_intent
from app.security.security_classifier import classify_security
from app.security.sensitive_detector import detect_sensitive_data
from app.security.semantic_classifier import classify_memory
from app.security.explainability import build_explanation


def evaluate_security(text: str, db=None, user_id=None):
    intent_result = classify_intent(text, db=db, user_id=user_id)
    security_result = classify_security(text)
    sensitive_result = detect_sensitive_data(text)
    classification_result = classify_memory(text)

    decision = security_result["decision"]
    risk_score = security_result["risk_score"]

    if sensitive_result["decision"] == "BLOCK":
        decision = "BLOCK"
        security_result["attack_type"] = "MEMORY_POISONING"
        security_result["risk_level"] = "HIGH"

    elif security_result["decision"] == "BLOCK":
        decision = "BLOCK"

    elif security_result["decision"] == "ALLOW_WITH_WARNING":
        decision = "ALLOW_WITH_WARNING"

    explanation = build_explanation(
        intent_result=intent_result,
        security_result=security_result,
        final_decision=decision,
    )

    return {
        "input": text,
        "intent": intent_result["intent"],
        "intent_confidence": intent_result["confidence"],
        "operation": intent_result["operation"],
        "operation_confidence": intent_result["confidence"],
        "operation_scores": intent_result.get("scores", {}),
        "category": classification_result["category"],
        "category_confidence": classification_result["confidence"],
        "attack_type": security_result["attack_type"],
        "attack_confidence": security_result["confidence"],
        "risk_level": security_result["risk_level"],
        "threat": (
            security_result["attack_type"]
            if security_result["attack_type"] != "SAFE"
            else "NONE"
        ),
        "risk_score": risk_score,
        "sensitive_type": sensitive_result["type"],
        "memory_poison_type": (
            security_result["attack_type"]
            if security_result["attack_type"] == "MEMORY_POISONING"
            else None
        ),
        "tool_policy_type": (
            security_result["attack_type"]
            if security_result["attack_type"] == "TOOL_MANIPULATION"
            else None
        ),
        "decision": decision,
        "explanation": explanation,
    }
