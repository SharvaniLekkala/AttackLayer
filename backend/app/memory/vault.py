from sqlalchemy.orm import Session

from app.database.models import Memory

from app.memory.embedding_service import (
    generate_embedding
)

from app.memory.vector_storage import (
    add_memory_embedding
)

from app.security.security_gateway import (
    evaluate_security
)

from app.security.memory_conflict_engine import (
    detect_conflict
)

from app.audit.logger import (
    log_security_event
)


def create_memory(
    db,
    user_id,
    fact
):

    # ==========================
    # Security Evaluation
    # ==========================

    security_result = evaluate_security(
        fact
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

    # ==========================
    # Blocked Content
    # ==========================

    if security_result["decision"] == "BLOCK":

        return {

            "status": "blocked",

            "security":
                security_result
        }

    # ==========================
    # Conflict Detection
    # ==========================

    existing_memory = detect_conflict(

    db=db,

    user_id=user_id,

    fact=fact,

    category=
        security_result["category"]
)

    new_version = 1

    conflict_detected = False

    if existing_memory:

        conflict_detected = True

        existing_memory.active = False

        db.commit()

        new_version = (
            existing_memory.version + 1
        )

    # ==========================
    # Create Memory
    # ==========================

    memory = Memory(

        user_id=user_id,

        fact=fact,

        category=
            security_result["category"],

        version=
            new_version,

        active=True
    )

    db.add(memory)

    db.commit()

    db.refresh(memory)

    # ==========================
    # Store Embedding
    # ==========================

    embedding = generate_embedding(
        fact
    )

    add_memory_embedding(

        memory.id,

        fact,

        embedding
    )

    # ==========================
    # Response
    # ==========================

    return {

        "status": "stored",

        "memory_id":
            memory.id,

        "version":
            memory.version,

        "conflict_detected":
            conflict_detected,

        "security":
            security_result
    }


def get_all_memories(
    db: Session
):

    return db.query(
        Memory
    ).all()


def get_memory_by_id(

    db: Session,

    memory_id: int

):

    return (

        db.query(Memory)

        .filter(
            Memory.id == memory_id
        )

        .first()

    )


def archive_memory(

    db: Session,

    memory_id: int

):

    memory = (

        db.query(Memory)

        .filter(
            Memory.id == memory_id
        )

        .first()

    )

    if not memory:

        return None

    memory.active = False

    db.commit()

    db.refresh(memory)

    return memory