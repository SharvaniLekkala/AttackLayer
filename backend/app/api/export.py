import tempfile

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import pandas as pd

from app.database.session import get_db
from app.database.models import AuditEvent, Memory, MemoryHistory

router = APIRouter(prefix="/export", tags=["Export"])


def _to_excel_response(df, filename, sheet_name):
    tmp = tempfile.NamedTemporaryFile(
        suffix=".xlsx", delete=False
    )
    tmp.close()
    df.to_excel(tmp.name, index=False, sheet_name=sheet_name)
    return FileResponse(
        tmp.name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=filename,
    )


@router.get("/audit-excel")
def export_audit(db: Session = Depends(get_db)):
    events = db.query(AuditEvent).order_by(AuditEvent.id.desc()).all()
    rows = []
    for e in events:
        rows.append({
            "id": e.id,
            "time": e.created_at.isoformat() if e.created_at else "",
            "prompt": e.payload,
            "operation": e.operation,
            "intent": getattr(e, "intent", ""),
            "intent_confidence": getattr(e, "intent_confidence", 0.0),
            "attack_type": getattr(e, "attack_type", ""),
            "attack_confidence": getattr(e, "attack_confidence", 0.0),
            "threat": e.threat,
            "risk_score": e.risk_score,
            "risk_level": getattr(e, "risk_level", ""),
            "decision": e.decision,
            "final_decision": getattr(e, "final_decision", e.decision),
            "retrieved_memories": getattr(e, "retrieved_memories", ""),
            "memories_used": getattr(e, "memories_used", ""),
            "poison_detected": getattr(e, "poison_detected", False),
            "quarantine_status": getattr(e, "quarantine_status", ""),
            "response_confidence": getattr(e, "response_confidence", 0.0),
            "memory_confidence": getattr(e, "memory_confidence", 0.0),
            "security_confidence": getattr(e, "security_confidence", 0.0),
            "execution_time_ms": getattr(e, "execution_time_ms", 0.0),
            "explanation": getattr(e, "explanation", ""),
        })
    df = pd.DataFrame(rows)
    return _to_excel_response(df, "audit_events.xlsx", "Audit Events")


@router.get("/memory-excel")
def export_memory(db: Session = Depends(get_db)):
    memories = db.query(Memory).order_by(Memory.id.desc()).all()
    rows = []
    for m in memories:
        rows.append({
            "id": m.id,
            "user_id": m.user_id,
            "fact": m.fact,
            "category": m.category,
            "trust_score": m.trust_score,
            "confidence_score": m.confidence_score,
            "conflict_score": m.conflict_score,
            "poison_score": m.poison_score,
            "risk_score": m.risk_score,
            "importance_score": getattr(m, "importance_score", 0.5),
            "verification_count": getattr(m, "verification_count", 0),
            "conflict_count": getattr(m, "conflict_count", 0),
            "usage_count": getattr(m, "usage_count", 0),
            "attack_type": m.attack_type,
            "status": getattr(m, "status", "ACTIVE"),
            "source": m.source,
            "memory_version": m.memory_version,
            "active": m.active,
            "created_at": m.created_at.isoformat() if m.created_at else "",
            "updated_at": m.updated_at.isoformat() if m.updated_at else "",
        })
    df = pd.DataFrame(rows)
    return _to_excel_response(df, "memory_vault.xlsx", "Memory Vault")


@router.get("/history-excel")
def export_history(db: Session = Depends(get_db)):
    history = db.query(MemoryHistory).order_by(MemoryHistory.id.desc()).all()
    rows = []
    for h in history:
        rows.append({
            "id": h.id,
            "memory_id": h.memory_id,
            "user_id": h.user_id,
            "old_fact": h.old_fact,
            "new_fact": h.new_fact,
            "category": h.category,
            "old_version": h.old_version,
            "new_version": h.new_version,
            "created_at": h.created_at.isoformat() if h.created_at else "",
        })
    df = pd.DataFrame(rows)
    return _to_excel_response(df, "memory_history.xlsx", "Memory History")
