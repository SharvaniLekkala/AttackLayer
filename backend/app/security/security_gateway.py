from app.security.intent_classifier import classify_intent
from app.security.security_classifier import classify_security
from app.security.sensitive_detector import detect_sensitive_data
from app.security.semantic_classifier import (
    classify_memory,
    classify_memory_type,
)
from app.security.explainability import build_explanation


def evaluate_security(text: str, db=None, user_id=None):
    intent_result = classify_intent(text, db=db, user_id=user_id)
    classification_result = classify_memory(text)
    memory_type_result = classify_memory_type(text)
    category = classification_result["category"]

    security_result = classify_security(text, category=category)
    sensitive_result = detect_sensitive_data(text)
    decision = security_result["decision"]
    risk_score = security_result["risk_score"]

    if sensitive_result["decision"] == "BLOCK":
        decision = "BLOCK"
        security_result["attack_type"] = "MEMORY_POISONING"
        security_result["risk_level"] = "HIGH"
        intent_result["intent"] = "SENSITIVE_DATA"
        intent_result["operation"] = "GENERAL_CHAT"
        intent_result["confidence"] = max(intent_result["confidence"], 0.99)

    elif security_result["decision"] == "BLOCK":
        decision = "BLOCK"
        if security_result["attack_type"] == "PROMPT_INJECTION":
            intent_result["intent"] = "PROMPT_INJECTION"
            intent_result["operation"] = "GENERAL_CHAT"
            intent_result["confidence"] = max(intent_result["confidence"], 0.99)

    elif security_result["decision"] == "ALLOW_WITH_WARNING":
        decision = "ALLOW_WITH_WARNING"

    benign_categories = {
        "FOOD_PREFERENCE", "CODING_PREFERENCE", "PROFESSION", "LOCATION",
        "PERSONAL_INFO", "CAREER", "STUDY_DOMAIN", "GENERAL_FACT", "GENERAL",
    }
    if (
        category in benign_categories
        and security_result["attack_type"] in ("SAFE", "SOCIAL_ENGINEERING", "SUSPICIOUS")
        and decision != "BLOCK"
    ):
        security_result["attack_type"] = "SAFE"
        decision = "ALLOW"
        risk_score = 0.0

    explanation = build_explanation(
        intent_result=intent_result,
        security_result=security_result,
        final_decision=decision,
    )

    threat = (
        security_result["attack_type"]
        if security_result["attack_type"] != "SAFE"
        else "NONE"
    )

    return {
        "input": text,
        "intent": intent_result["intent"],
        "intent_confidence": intent_result["confidence"],
        "operation": intent_result["operation"],
        "operation_confidence": intent_result["confidence"],
        "operation_scores": intent_result.get("scores", {}),
        "category": category,
        "category_confidence": classification_result["confidence"],
        "memory_type": memory_type_result["memory_type"],
        "memory_type_confidence": memory_type_result["confidence"],
        "attack_type": security_result["attack_type"],
        "attack_confidence": security_result["confidence"],
        "risk_level": security_result["risk_level"],
        "threat": threat,
        "risk_score": risk_score,
        "sensitive_type": sensitive_result["type"],
        "memory_poison_type": (
            security_result["attack_type"]
            if security_result["attack_type"] == "MEMORY_POISONING"
            else None
        ),
        "tool_policy_type": (
            security_result["attack_type"]
            if security_result["attack_type"] in ("TOOL_MANIPULATION", "TOOL_POLICY_MANIPULATION")
            else None
        ),
        "mitigation": security_result.get("mitigation", "NONE"),
        "decision": decision,
        "explanation": explanation,
    }
