from app.database.models import (
    MemoryHistory
)


def log_memory_history(

    db,

    old_memory,

    new_fact,

    new_version

):

    history = MemoryHistory(

        memory_id=
            old_memory.id,

        user_id=
            old_memory.user_id,

        old_fact=
            old_memory.fact,

        new_fact=
            new_fact,

        category=
            old_memory.category,

        old_version=
            old_memory.version,

        new_version=
            new_version

    )

    db.add(history)

    db.commit()

    db.refresh(history)

    return history