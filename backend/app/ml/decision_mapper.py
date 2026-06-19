def map_decision(prediction, confidence):
    """
    Maps ML model prediction + confidence to a security decision.

    Rules:
        prediction == 0  →  ALLOW  (always, regardless of confidence)
        prediction == 1:
            confidence >= 0.90  →  BLOCK
            0.75 <= confidence < 0.90  →  QUARANTINE
            confidence < 0.75  →  REVIEW
    """

    if prediction == 0:
        return "ALLOW"

    # prediction == 1 (attack detected)
    if confidence >= 0.90:
        return "BLOCK"

    if confidence >= 0.75:
        return "QUARANTINE"

    return "REVIEW"