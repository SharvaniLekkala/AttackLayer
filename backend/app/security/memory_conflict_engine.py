from app.database.models import (
    Memory
)


def detect_conflict(
    db,
    user_id,
    fact,
    category
):

    existing_memories = (

        db.query(Memory)

        .filter(
            Memory.user_id == user_id,
            Memory.category == category,
            Memory.active == True
        )

        .all()
    )

    if not existing_memories:

        return None

    fact_normalized = (
        fact.strip()
        .lower()
    )

    for memory in existing_memories:

        existing_fact = (
            memory.fact.strip()
            .lower()
        )

        if existing_fact != fact_normalized:

            return memory

    return None