from app.database.models import (
    PreferenceEvent
)


def log_preference_event(
    db,
    user_id,
    memory_id,
    old_fact,
    new_fact,
    category,
    stability_score,
    drift_score,
    is_legitimate_update,
    attack_type="PREFERENCE_UPDATE"
):

    event = PreferenceEvent(

        user_id=user_id,

        memory_id=memory_id,

        old_fact=old_fact,

        new_fact=new_fact,

        category=category,

        stability_score=stability_score,

        drift_score=drift_score,

        is_legitimate_update=is_legitimate_update,

        attack_type=attack_type

    )

    db.add(event)

    db.commit()

    db.refresh(event)

    return event
