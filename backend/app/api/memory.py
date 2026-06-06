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

    db: Session = Depends(
        get_db
    )

):

    memories = get_all_memories(

        db

    )

    result = []

    for memory in memories:

        result.append(

            {

                "id":

                    memory.id,

                "fact":

                    memory.fact,

                "category":

                    memory.category,

                "trust_score":

                    round(

                        memory.trust_score,

                        4

                    ),

                "risk_score":

                    round(

                        memory.risk_score,

                        4

                    ),

                "version":

                    memory.version,

                "status":

                    "ACTIVE"

                    if

                    memory.active

                    else

                    "INACTIVE",

                "source":

                    memory.source

            }

        )

    return result


@router.post(
    "/archive/{memory_id}"
)
def archive(

    memory_id: int,

    db: Session = Depends(
        get_db
    )

):

    return archive_memory(

        db,

        memory_id

    )


@router.get(
    "/history/{memory_id}"
)
def history(

    memory_id: int,

    db: Session = Depends(
        get_db
    )

):

    history = get_memory_history(

        db,

        memory_id

    )

    result = []

    for item in history:

        result.append(

            {

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

            }

        )

    return result


@router.get(
    "/history"
)
def full_history(

    db: Session = Depends(
        get_db
    )

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

        result.append(

            {

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

            }

        )

    return result