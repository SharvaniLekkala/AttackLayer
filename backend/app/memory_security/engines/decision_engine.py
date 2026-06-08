from app.memory_security.constants import (
    ALLOW,
    ALLOW_WITH_WARNING,
    QUARANTINE,
    BLOCK
)


class DecisionEngine:

    @staticmethod
    def decide(
        poison_score: float,
        conflict_score: float,
        trust_score: float
    ):

        if poison_score >= 0.85:
            return BLOCK

        if poison_score >= 0.65:
            return QUARANTINE

        if conflict_score >= 0.60:
            return ALLOW_WITH_WARNING

        if trust_score <= 0.30:
            return QUARANTINE

        return ALLOW