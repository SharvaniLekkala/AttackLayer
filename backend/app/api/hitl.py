from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import AuditEvent
from app.database.models import (
    AuditEvent,
    Memory
)

from app.memory.embedding_service import (
    generate_embedding
)

from app.memory.vector_storage import (
    add_memory_embedding
)

router = APIRouter(prefix="/hitl", tags=["HITL"])


@router.get("/queue")
def get_hitl_queue(db: Session = Depends(get_db)):
    """
    Get all audit events that are pending human review (ALLOW_WITH_WARNING).
    """
    events = (
        db.query(AuditEvent)
        .filter(AuditEvent.final_decision == "ALLOW_WITH_WARNING")
        .order_by(AuditEvent.id.desc())
        .all()
    )

    import json
    result = []
    for event in events:
        explanation = event.explanation or {}
        if isinstance(explanation, str):
            try:
                explanation = json.loads(explanation)
            except Exception:
                explanation = {}
                
        # Ensure it hasn't been approved/rejected already
        if "human_decision" in explanation:
            continue
            
        result.append({
            "id": event.id,
            "prompt": event.payload,
            "threat_type": event.threat if event.threat else "NONE",
            "severity": event.risk_level if event.risk_level else "LOW",
            "detection_reason": explanation.get("security_result", {}).get("decision", "UNKNOWN"),
            "timestamp": event.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "human_decision": explanation.get("human_decision")
        })

    return result


@router.post("/approve/{request_id}")
def approve_hitl_request(request_id: int, db: Session = Depends(get_db)):
    """
    Approve a HITL request: change final_decision to ALLOW and add note.
    """
    event = db.query(AuditEvent).filter(AuditEvent.id == request_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Request not found")
    if event.final_decision != "ALLOW_WITH_WARNING":
        raise HTTPException(status_code=400, detail="Request is not pending review")

    from datetime import datetime
    # Update the event
    event.final_decision = "ALLOW"
    # Update explanation to note human approval
    import json
    explanation = event.explanation or {}
    if isinstance(explanation, str):
        try:
            explanation = json.loads(explanation)
        except Exception:
            explanation = {}
            
    explanation["human_decision"] = "APPROVED"
    explanation["human_decision_timestamp"] = datetime.utcnow().isoformat()
    event.explanation = json.dumps(explanation)

    # ------------------------
    # Activate pending memory
    # ------------------------

    if event.memory_id:

        memory = (
            db.query(Memory)
            .filter(
                Memory.id == event.memory_id
            )
            .first()
        )

        if memory:

            memory.active = True

            memory.status = "ACTIVE"

            embedding = generate_embedding(
                memory.fact
            )

            add_memory_embedding(

                memory.id,

                memory.fact,

                embedding

            )

    db.commit()
    db.refresh(event)

    final_response = "Got it. I've updated your memory."
    if event.memory_id:
        memory = db.query(Memory).filter(Memory.id == event.memory_id).first()
        if not memory or memory.status != "ACTIVE":
            final_response = "Got it. I've updated your memory."

    return {"status": "approved", "request_id": request_id, "response": final_response}


@router.post("/reject/{request_id}")
def reject_hitl_request(request_id: int, db: Session = Depends(get_db)):
    """
    Reject a HITL request: change final_decision to BLOCK and add note.
    """
    event = db.query(AuditEvent).filter(AuditEvent.id == request_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Request not found")
    if event.final_decision != "ALLOW_WITH_WARNING":
        raise HTTPException(status_code=400, detail="Request is not pending review")

    from datetime import datetime
    # Update the event
    event.final_decision = "BLOCK"
    # Update explanation to note human rejection
    import json
    explanation = event.explanation or {}
    if isinstance(explanation, str):
        try:
            explanation = json.loads(explanation)
        except Exception:
            explanation = {}
            
    explanation["human_decision"] = "REJECTED"
    explanation["human_decision_timestamp"] = datetime.utcnow().isoformat()
    event.explanation = json.dumps(explanation)

    # ------------------------
    # Remove pending memory
    # ------------------------

    if event.memory_id:

        memory = (
            db.query(Memory)
            .filter(
                Memory.id == event.memory_id
            )
            .first()
        )

        if memory:

            db.delete(memory)

    db.commit()

    db.refresh(event)

    return {"status": "rejected", "request_id": request_id}
@router.get("/status/{request_id}")
def get_hitl_status(
    request_id: int,
    db: Session = Depends(get_db)
):

    event = (
        db.query(AuditEvent)
        .filter(
            AuditEvent.id == request_id
        )
        .first()
    )

    if not event:
        raise HTTPException(
            status_code=404,
            detail="Request not found"
        )

    import json

    explanation = event.explanation or {}

    if isinstance(explanation, str):
        try:
            explanation = json.loads(
                explanation
            )
        except Exception:
            explanation = {}

    human_decision = explanation.get(
        "human_decision"
    )

    if not human_decision:
        return {
            "resolved": False
        }

    if human_decision == "APPROVED":
        if event.memory_id:
            response = "✓ Approved. Your memory has been saved and is now active."
        else:
            response = "✓ Your request was approved by a human reviewer and has been processed."
    else:
        if event.memory_id:
            response = "⚠ Rejected. The memory update was blocked by human review."
        else:
            response = "⚠ Your request was reviewed and rejected by a human reviewer. It has been blocked."

    return {
        "resolved": True,
        "decision": human_decision,
        "response": response
    }
@router.get("/resolved")
def get_resolved_hitl_items(db: Session = Depends(get_db)):
    """
    Get all HITL requests that have already been approved or rejected.
    """
    import json
    events = (
        db.query(AuditEvent)
        .filter(AuditEvent.final_decision.in_(["ALLOW", "BLOCK"]))
        .order_by(AuditEvent.id.desc())
        .limit(50)
        .all()
    )

    result = []
    for event in events:
        explanation = event.explanation or {}
        if isinstance(explanation, str):
            try:
                explanation = json.loads(explanation)
            except Exception:
                explanation = {}

        human_decision = explanation.get("human_decision")
        if not human_decision:
            continue  # was auto-allowed/blocked, not HITL

        result.append({
            "id": event.id,
            "prompt": event.payload,
            "status": "approved" if human_decision == "APPROVED" else "rejected",
            "response": "Got it. I've updated your memory." if human_decision == "APPROVED"
                        else "Request rejected and blocked by security policy.",
            "timestamp": event.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        })

    return result