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
from app.security.instruction_detector import (
    detect_instruction_attack
)
from app.security.secret_request_detector import (
    detect_secret_request
)
from app.security.memory_poison_detector import (
    detect_memory_poisoning
)
def evaluate_security(text: str):

    request_result = analyze_request(text)

    threat_result = detect_threat(text)

    sensitive_result = detect_sensitive_data(text)

    classification_result = classify_memory(text)
    secret_request_result = (

    detect_secret_request(

        text

    )

)
    instruction_result = (

    detect_instruction_attack(

        text

    )

)
    poison_result = (

    detect_memory_poisoning(

        text

    )

)
    decision = "ALLOW"

    risk_score = threat_result["risk_score"]

    # Sensitive detector always wins

    if sensitive_result["decision"] == "BLOCK":

        decision = "BLOCK"

    elif threat_result["decision"] == "BLOCK":

        decision = "BLOCK"

    elif instruction_result["decision"] == "BLOCK":

        decision = "BLOCK"

    elif secret_request_result["decision"] == "BLOCK":

        decision = "BLOCK"

    elif poison_result["decision"] == "BLOCK":

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

"instruction_type":

    instruction_result[
        "type"
    ],
    "secret_request_type":

    secret_request_result[
        "type"
    ],
    "memory_poison_type":

    poison_result[
        "type"
    ],
        "decision":
            decision
    }