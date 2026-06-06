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

from app.security.trust_engine import (
    calculate_trust
)
from app.audit.history_logger import (
    log_memory_history
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

        new_version = (

            existing_memory.version

            +

            1

        )

        log_memory_history(

            db=db,

            old_memory=
                existing_memory,

            new_fact=
                fact,

            new_version=
                new_version

        )

        existing_memory.active = False

        db.commit()
    trust_score = calculate_trust(

    source="USER",

    security_decision=

        security_result[
            "decision"
        ],

    category_confidence=

        security_result[
            "category_confidence"
        ],

    conflict_detected=

        conflict_detected,

    version=

        new_version,

    attack_type=

        security_result[
            "threat"
        ]

)
    # ==========================
    # Create Memory
    # ==========================

    memory = Memory(

    user_id=user_id,

    fact=fact,

    category=
        security_result[
            "category"
        ],

    trust_score=
        trust_score,

    risk_score=
        security_result[
            "risk_score"
        ],

    source="USER",

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

from app.database.models import (
    MemoryHistory
)


def get_memory_history(

    db,

    memory_id

):

    history = (

        db.query(

            MemoryHistory

        )

        .filter(

            MemoryHistory.memory_id

            ==

            memory_id

        )

        .all()

    )

    return history