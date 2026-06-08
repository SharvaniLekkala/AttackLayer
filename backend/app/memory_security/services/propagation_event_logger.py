from app.database.models import (
    PropagationEvent
)


def log_propagation_event(
    db,
    memory_id,
    origin_agent,
    target_agent,
    propagation_path,
    spread_score,
    fact="",
    poison_score=0.0,
    attack_type="NONE",
    spread_percentage=0.0,
    decision="ALLOW",
    root_memory_id=None
):

    event = PropagationEvent(

        memory_id=memory_id,

        origin_agent=origin_agent,

        target_agent=target_agent,

        propagation_path=propagation_path,

        spread_score=spread_score,

        fact=fact,

        poison_score=poison_score,

        attack_type=attack_type,

        spread_percentage=spread_percentage,

        decision=decision,

        root_memory_id=root_memory_id,

    )

    db.add(event)

    db.commit()

    db.refresh(event)

    return event
