from sqlalchemy.orm import Session

from app.database.models import Memory
from app.memory.embedding_service import generate_embedding

from app.memory.vector_storage import (
    add_memory_embedding
)
from app.security.security_gateway import (
    evaluate_security
)

from app.audit.logger import (
    log_security_event
)
def create_memory(
    db,
    user_id,
    fact
):

    security_result = (
        evaluate_security(fact)
    )

    log_security_event(

        db=db,

        operation="WRITE",

        decision=
            security_result["decision"],

        threat=
            security_result["threat"],

        risk_score=
            security_result["risk_score"],

        payload=fact
    )

    if security_result["decision"] == "BLOCK":

        return {

            "status": "blocked",

            "security":
                security_result
        }

    memory = Memory(

        user_id=user_id,

        fact=fact,

        category=
            security_result["category"]
    )

    db.add(memory)

    db.commit()

    db.refresh(memory)

    return {

        "status": "stored",

        "memory_id":
            memory.id,

        "security":
            security_result
    }

def get_all_memories(db: Session):

    return db.query(Memory).all()


def get_memory_by_id(
    db: Session,
    memory_id: int
):

    return (
        db.query(Memory)
        .filter(Memory.id == memory_id)
        .first()
    )


def archive_memory(
    db: Session,
    memory_id: int
):

    memory = (
        db.query(Memory)
        .filter(Memory.id == memory_id)
        .first()
    )

    if not memory:
        return None

    memory.active = False

    db.commit()
    db.refresh(memory)

    return memory