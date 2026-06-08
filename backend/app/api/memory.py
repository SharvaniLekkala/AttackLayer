from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.session import (
    get_db
)

from app.memory.vault import (
    get_all_memories,
    archive_memory,
    get_memory_history
)

from app.database.models import (
    MemoryHistory
)

router = APIRouter(
    prefix="/memory",
    tags=["Memory"]
)


@router.get("/all")
def all_memories(
    db: Session = Depends(get_db)
):

    memories = get_all_memories(db)

    result = []

    for memory in memories:

        result.append({

            "id": memory.id,

            "user_id": memory.user_id,

            "fact": memory.fact,

            "category": memory.category,

            "trust_score": round(
                memory.trust_score,
                4
            ),

            "confidence_score": round(
                memory.confidence_score,
                4
            ),

            "conflict_score": round(
                memory.conflict_score,
                4
            ),

            "poison_score": round(
                memory.poison_score,
                4
            ),

            "risk_score": round(
                memory.risk_score,
                4
            ),

            "attack_type":
                memory.attack_type,

            "decision":
                memory.final_decision,

            "memory_version":
                memory.memory_version,

            "verified":
                memory.verified,

            "poison_flag":
                memory.poison_flag,

            "status":
                "ACTIVE"
                if memory.active
                else "INACTIVE",

            "source":
                memory.source
        })

    return result


@router.post("/archive/{memory_id}")
def archive(
    memory_id: int,
    db: Session = Depends(get_db)
):

    return archive_memory(
        db,
        memory_id
    )


@router.get("/history/{memory_id}")
def history(
    memory_id: int,
    db: Session = Depends(get_db)
):

    history = get_memory_history(
        db,
        memory_id
    )

    result = []

    for item in history:

        result.append({

            "id":
                item.id,

            "old_fact":
                item.old_fact,

            "new_fact":
                item.new_fact,

            "category":
                item.category,

            "old_version":
                item.old_version,

            "new_version":
                item.new_version,

            "time":
                item.created_at.strftime(
                    "%H:%M:%S"
                )

        })

    return result


@router.get("/history")
def full_history(
    db: Session = Depends(get_db)
):

    records = (

        db.query(
            MemoryHistory
        )

        .order_by(
            MemoryHistory.id.desc()
        )

        .all()

    )

    result = []

    for item in records:

        result.append({

            "memory_id":
                item.memory_id,

            "old_fact":
                item.old_fact,

            "new_fact":
                item.new_fact,

            "category":
                item.category,

            "old_version":
                item.old_version,

            "new_version":
                item.new_version,

            "time":
                item.created_at.strftime(
                    "%H:%M:%S"
                )

        })

    return result