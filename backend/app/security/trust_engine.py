def calculate_trust(

    source,
    security_decision,
    category_confidence,
    conflict_detected,
    version,
    attack_type=None

):

    trust = 1.0

    confidence_score = category_confidence

    conflict_score = 0.0

    poison_score = 0.0

    # -------------------
    # Source
    # -------------------

    if source == "USER":

        trust -= 0.05

    # -------------------
    # Confidence
    # -------------------

    trust *= confidence_score

    # -------------------
    # Conflict
    # -------------------

    if conflict_detected:

        conflict_score = 0.60

        trust -= 0.05

    # -------------------
    # Versions
    # -------------------

    if version > 1:

        trust -= (

            version - 1

        ) * 0.02

    # -------------------
    # Security
    # -------------------

    if security_decision == "BLOCK":

        trust -= 0.20

    # -------------------
    # Attack Penalties
    # -------------------

    if attack_type == "MEMORY_POISONING":

        poison_score = 0.90

        trust -= 0.25

    elif attack_type == "PROMPT_INJECTION":

        poison_score = 0.70

        trust -= 0.20

    elif attack_type == "PASSWORD":

        poison_score = 0.85

        trust -= 0.25

    elif attack_type == "TOOL_POLICY_POISONING":

        poison_score = 0.92

        trust -= 0.30

    elif attack_type == "PROPAGATION_ATTACK":

        poison_score = 0.88

        trust -= 0.28

    if trust < 0:

        trust = 0

    if trust > 1:

        trust = 1

    return {

        "trust_score": round(
            trust,
            4
        ),

        "confidence_score":
            confidence_score,

        "conflict_score":
            conflict_score,

        "poison_score":
            poison_score
    }