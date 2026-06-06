def calculate_trust(

    source,

    security_decision,

    category_confidence,

    conflict_detected,

    version,

    attack_type=None

):

    trust = 1.0

    # --------------------------
    # Source
    # --------------------------

    if source == "USER":

        trust -= 0.05

    # --------------------------
    # Classification confidence
    # --------------------------

    trust *= category_confidence

    # --------------------------
    # Conflict
    # --------------------------

    if conflict_detected:

        trust -= 0.05

    # --------------------------
    # Versions
    # --------------------------

    if version > 1:

        trust -= (

            version - 1

        ) * 0.02

    # --------------------------
    # Security violations
    # --------------------------

    if security_decision == "BLOCK":

        trust -= 0.20

    # --------------------------
    # Attack penalties
    # --------------------------

    if attack_type == "PASSWORD":

        trust -= 0.25

    elif attack_type == "PROMPT_INJECTION":

        trust -= 0.20

    elif attack_type == "SECRET_RETRIEVAL":

        trust -= 0.20

    elif attack_type == "MEMORY_POISONING":

        trust -= 0.25

    if trust < 0:

        trust = 0

    if trust > 1:

        trust = 1

    return round(

        trust,

        4

    )