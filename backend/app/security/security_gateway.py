from app.security.request_analyzer import (
    analyze_request
)

from app.security.threat_detector import (
    detect_threat
)

from app.security.sensitive_detector import (
    detect_sensitive_data
)

from app.security.semantic_classifier import (
    classify_memory
)


def evaluate_security(text: str):

    request_result = analyze_request(text)

    threat_result = detect_threat(text)

    sensitive_result = detect_sensitive_data(text)

    classification_result = classify_memory(text)

    decision = "ALLOW"

    risk_score = threat_result["risk_score"]

    # Sensitive detector always wins

    if sensitive_result["decision"] == "BLOCK":

        decision = "BLOCK"

    elif threat_result["decision"] == "BLOCK":

        decision = "BLOCK"

    elif threat_result["decision"] == "REVIEW":

        decision = "REVIEW"

    return {

        "input": text,

        "operation": request_result["operation"],

        "operation_confidence":
            request_result["confidence"],

        "category":
            classification_result["category"],

        "category_confidence":
            classification_result["confidence"],

        "threat":
            threat_result["threat"],

        "risk_score":
            risk_score,

        "sensitive_type":
            sensitive_result["type"],

        "decision":
            decision
    }