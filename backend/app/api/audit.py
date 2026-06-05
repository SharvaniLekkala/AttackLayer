from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.session import (
    get_db
)

from app.database.models import (
    AuditEvent
)

router = APIRouter(
    prefix="/audit",
    tags=["Audit"]
)


@router.get("/events")
def get_events(

    db: Session = Depends(get_db)

):

    return (
        db.query(AuditEvent)
        .order_by(
            AuditEvent.id.desc()
        )
        .all()
    )