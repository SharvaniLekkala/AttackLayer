from app.database.models import (
    QuarantineMemory
)


def quarantine_memory(
    db,
    user_id,
    fact,
    category,
    attack_type,
    reason,
    risk_score,
    poison_score
):

    record = QuarantineMemory(

        user_id=user_id,

        fact=fact,

        category=category,

        attack_type=attack_type,

        reason=reason,

        risk_score=risk_score,

        poison_score=poison_score

    )

    db.add(record)

    db.commit()

    db.refresh(record)

    return record