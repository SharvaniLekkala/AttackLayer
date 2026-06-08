from app.database.models import (
    PoisonEvent
)


def log_poison_event(
    db,
    attack_type,
    poison_score,
    decision,
    details,
    memory_id=None
):

    event = PoisonEvent(

        memory_id=memory_id,

        attack_type=attack_type,

        poison_score=poison_score,

        decision=decision,

        details=details

    )

    db.add(event)

    db.commit()

    db.refresh(event)

    return event