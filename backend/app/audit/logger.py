from app.database.models import (
    AuditEvent
)


def log_security_event(

    db,

    operation,
    decision,
    threat,
    risk_score,
    payload

):

    event = AuditEvent(

        operation=operation,

        decision=decision,

        threat=threat,

        risk_score=risk_score,

        payload=payload
    )

    db.add(event)

    db.commit()

    db.refresh(event)

    return event