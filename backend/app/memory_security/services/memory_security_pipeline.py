from app.memory_security.engines.decision_engine import (
    DecisionEngine
)


class MemorySecurityPipeline:

    @staticmethod
    def evaluate(
        trust_score: float,
        confidence_score: float,
        conflict_score: float,
        poison_score: float
    ):

        decision = DecisionEngine.decide(
            poison_score=poison_score,
            conflict_score=conflict_score,
            trust_score=trust_score
        )

        return {

            "trust_score":
                trust_score,

            "confidence_score":
                confidence_score,

            "conflict_score":
                conflict_score,

            "poison_score":
                poison_score,

            "decision":
                decision
        }