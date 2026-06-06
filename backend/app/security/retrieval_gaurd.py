from app.security.sensitive_detector import (
    detect_sensitive_data
)

from app.security.threat_detector import (
    detect_threat
)


MINIMUM_TRUST_SCORE = 0.30

MAXIMUM_RISK_SCORE = 0.80


def filter_memories(
    memories,
    query
):

    query_threat = detect_threat(
        query
    )

    if (

        query_threat["threat"]

        ==

        "RETRIEVAL_ABUSE"

    ):

        return {

            "allowed_memories": [],

            "blocked_memories": [],

            "blocked_reasons": [

                "Retrieval abuse detected"

            ]
        }

    allowed_memories = []

    blocked_memories = []

    blocked_reasons = []

    for memory in memories:

        # -------------------------
        # Inactive Memory
        # -------------------------

        if not memory.active:

            blocked_memories.append(
                memory
            )

            blocked_reasons.append(

                f"Memory {memory.id} is inactive"

            )

            continue

        # -------------------------
        # Sensitive Content
        # -------------------------

        sensitive_result = (

            detect_sensitive_data(

                memory.fact

            )

        )

        if (

            sensitive_result["decision"]

            ==

            "BLOCK"

        ):

            blocked_memories.append(
                memory
            )

            blocked_reasons.append(

                f"Memory {memory.id} contains "

                f"{sensitive_result['type']}"

            )

            continue

        # -------------------------
        # Masked Content
        # -------------------------

        if (

            sensitive_result["decision"]

            ==

            "MASK"

        ):

            blocked_memories.append(
                memory
            )

            blocked_reasons.append(

                f"Memory {memory.id} "

                f"contains masked data"

            )

            continue

        # -------------------------
        # Risk Score
        # -------------------------

        if (

            memory.risk_score

            >=

            MAXIMUM_RISK_SCORE

        ):

            blocked_memories.append(
                memory
            )

            blocked_reasons.append(

                f"Memory {memory.id} "

                f"risk score too high"

            )

            continue

        # -------------------------
        # Trust Score
        # -------------------------

        if (

            memory.trust_score

            <

            MINIMUM_TRUST_SCORE

        ):

            blocked_memories.append(
                memory
            )

            blocked_reasons.append(

                f"Memory {memory.id} "

                f"trust score too low"

            )

            continue

        # -------------------------
        # Safe Memory
        # -------------------------

        allowed_memories.append(
            memory
        )

    return {

        "allowed_memories":

            allowed_memories,

        "blocked_memories":

            blocked_memories,

        "blocked_reasons":

            blocked_reasons
    }