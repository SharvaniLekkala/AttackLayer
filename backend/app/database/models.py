from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Float
from sqlalchemy import Boolean
from sqlalchemy import DateTime

from datetime import datetime

from app.database.session import Base


class Memory(Base):
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(String, nullable=False)

    fact = Column(String, nullable=False)

    category = Column(String, default="UNKNOWN")

    trust_score = Column(Float, default=0.5)

    risk_score = Column(Float, default=0.0)

    sensitivity_level = Column(String, default="LOW")

    source = Column(String, default="USER")

    version = Column(Integer, default=1)

    active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
class AuditEvent(Base):

    __tablename__ = "audit_events"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    operation = Column(
        String,
        nullable=False
    )

    decision = Column(
        String,
        nullable=False
    )

    threat = Column(
        String,
        nullable=False
    )

    risk_score = Column(
        Float,
        default=0.0
    )

    payload = Column(
        String,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )