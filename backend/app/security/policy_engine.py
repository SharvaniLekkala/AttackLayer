THREAT_SEVERITY = {

    "SAFE": 0.0,

    "PROMPT_INJECTION": 0.90,

    "MEMORY_POISONING": 1.00,

    "FACTUAL_POISONING": 0.90,

    "ROLE_OVERRIDE": 0.90,

    "SOCIAL_ENGINEERING": 0.85,

    "RETRIEVAL_ABUSE": 0.85,

    "CREDENTIAL_STORAGE": 1.00,

    "PII_STORAGE": 0.95
}


HARD_BLOCK_THREATS = {

    "CREDENTIAL_STORAGE",

    "MEMORY_POISONING"
}


REVIEW_THREATS = {

    "PROMPT_INJECTION",

    "ROLE_OVERRIDE",

    "RETRIEVAL_ABUSE",

    "SOCIAL_ENGINEERING",

    "FACTUAL_POISONING",

    "PII_STORAGE"
}


def evaluate_policy(
    threat: str,
    similarity_score: float
):

    severity = THREAT_SEVERITY.get(
        threat,
        0.0
    )

    risk_score = round(
        (
            0.6 * similarity_score
            +
            0.4 * severity
        ),
        4
    )

    if threat in HARD_BLOCK_THREATS:

        return {
            "decision": "BLOCK",
            "risk_score": risk_score
        }

    if threat in REVIEW_THREATS:

        if risk_score >= 0.75:

            return {
                "decision": "REVIEW",
                "risk_score": risk_score
            }

    return {
        "decision": "ALLOW",
        "risk_score": risk_score
    }