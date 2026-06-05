import re


PASSWORD_PATTERNS = [
    r"password\s*[:=]?\s*\S+",
]

API_KEY_PATTERNS = [
    r"api[_\s]?key\s*[:=]?\s*\S+",
]

TOKEN_PATTERNS = [
    r"token\s*[:=]?\s*\S+",
]

EMAIL_PATTERNS = [
    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
]


def detect_sensitive_data(text: str):

    lower_text = text.lower()

    for pattern in PASSWORD_PATTERNS:

        if re.search(pattern, lower_text):
            return {
                "type": "PASSWORD",
                "decision": "BLOCK"
            }

    for pattern in API_KEY_PATTERNS:

        if re.search(pattern, lower_text):
            return {
                "type": "API_KEY",
                "decision": "BLOCK"
            }

    for pattern in TOKEN_PATTERNS:

        if re.search(pattern, lower_text):
            return {
                "type": "TOKEN",
                "decision": "BLOCK"
            }

    for pattern in EMAIL_PATTERNS:

        if re.search(pattern, text):
            return {
                "type": "EMAIL",
                "decision": "MASK"
            }

    return {
        "type": None,
        "decision": "ALLOW"
    }