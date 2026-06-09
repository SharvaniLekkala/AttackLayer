from fastapi import APIRouter

from app.database.models import (
    AuditEvent,
    ClassificationStat,
    Memory,
    MemoryHistory,
    PoisonEvent,
    PreferenceEvent,
    PropagationEvent,
    QuarantineMemory,
    ReflectionLog,
    ToolPolicyEvent,
)
from app.database.session import SessionLocal
from app.memory.vector_storage import reset_memory_collection


router = APIRouter(prefix="/admin", tags=["Admin"])


@router.delete("/databases")
def clear_databases():
    db = SessionLocal()
    try:
        for model in (
            PropagationEvent,
            ToolPolicyEvent,
            PreferenceEvent,
            PoisonEvent,
            QuarantineMemory,
            MemoryHistory,
            ReflectionLog,
            ClassificationStat,
            AuditEvent,
            Memory,
        ):
            db.query(model).delete(synchronize_session=False)

        db.commit()
        reset_memory_collection()

        return {
            "status": "cleared",
            "message": "AttackLayer and Chroma memory data cleared.",
        }
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
