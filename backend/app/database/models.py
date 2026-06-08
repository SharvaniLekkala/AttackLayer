from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Float
from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey

from datetime import datetime

from app.database.session import Base


# =====================================================
# MEMORY VAULT
# =====================================================

class Memory(Base):
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(String, nullable=False)

    fact = Column(String, nullable=False)

    category = Column(String, default="UNKNOWN")

    # ------------------------------
    # Trust System
    # ------------------------------

    trust_score = Column(Float, default=0.50)

    confidence_score = Column(Float, default=0.50)

    conflict_score = Column(Float, default=0.0)

    poison_score = Column(Float, default=0.0)

    risk_score = Column(Float, default=0.0)

    # ------------------------------
    # Security
    # ------------------------------

    poison_flag = Column(Boolean, default=False)

    verified = Column(Boolean, default=False)

    attack_type = Column(String, default="NONE")

    sensitivity_level = Column(String, default="LOW")

    source = Column(String, default="USER")

    final_decision = Column(
        String,
        default="ALLOW"
    )

    # ------------------------------
    # Versioning
    # ------------------------------

    memory_version = Column(
        Integer,
        default=1
    )

    parent_memory_id = Column(
        Integer,
        nullable=True
    )

    active = Column(
        Boolean,
        default=True
    )

    preference_stability_score = Column(
        Float,
        nullable=True
    )

    preference_drift_score = Column(
        Float,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


# =====================================================
# PREFERENCE EVENTS
# =====================================================

class PreferenceEvent(Base):
    __tablename__ = "preference_events"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        String,
        nullable=False
    )

    memory_id = Column(
        Integer,
        nullable=True
    )

    old_fact = Column(
        String,
        nullable=False
    )

    new_fact = Column(
        String,
        nullable=False
    )

    category = Column(
        String,
        default="PREFERENCE"
    )

    stability_score = Column(
        Float,
        default=1.0
    )

    drift_score = Column(
        Float,
        default=0.0
    )

    is_legitimate_update = Column(
        Boolean,
        default=True
    )

    attack_type = Column(
        String,
        default="PREFERENCE_UPDATE"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# =====================================================
# TOOL POLICY EVENTS
# =====================================================

class ToolPolicyEvent(Base):
    __tablename__ = "tool_policy_events"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        String,
        nullable=False
    )

    memory_id = Column(
        Integer,
        nullable=True
    )

    policy_text = Column(
        String,
        nullable=False
    )

    violation_reason = Column(
        String,
        default=""
    )

    risk_score = Column(
        Float,
        default=0.0
    )

    decision = Column(
        String,
        nullable=False
    )

    unapproved_domains = Column(
        String,
        default=""
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# =====================================================
# MEMORY QUARANTINE
# =====================================================

class QuarantineMemory(Base):
    __tablename__ = "quarantine_memories"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        String,
        nullable=False
    )

    fact = Column(
        String,
        nullable=False
    )

    category = Column(
        String,
        default="UNKNOWN"
    )

    attack_type = Column(
        String,
        default="UNKNOWN"
    )

    reason = Column(
        String,
        nullable=False
    )

    risk_score = Column(
        Float,
        default=0.0
    )

    poison_score = Column(
        Float,
        default=0.0
    )

    review_status = Column(
        String,
        default="PENDING"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# =====================================================
# POISON EVENTS
# =====================================================

class PoisonEvent(Base):
    __tablename__ = "poison_events"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    memory_id = Column(
        Integer,
        nullable=True
    )

    attack_type = Column(
        String,
        nullable=False
    )

    poison_score = Column(
        Float,
        default=0.0
    )

    decision = Column(
        String,
        nullable=False
    )

    details = Column(
        String,
        default=""
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# =====================================================
# PROPAGATION EVENTS
# =====================================================

class PropagationEvent(Base):
    __tablename__ = "propagation_events"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    memory_id = Column(
        Integer,
        nullable=False
    )

    origin_agent = Column(
        String,
        nullable=False
    )

    target_agent = Column(
        String,
        nullable=False
    )

    propagation_path = Column(
        String,
        nullable=False
    )

    spread_score = Column(
        Float,
        default=0.0
    )

    fact = Column(
        String,
        default=""
    )

    poison_score = Column(
        Float,
        default=0.0
    )

    attack_type = Column(
        String,
        default="NONE"
    )

    spread_percentage = Column(
        Float,
        default=0.0
    )

    decision = Column(
        String,
        default="ALLOW"
    )

    root_memory_id = Column(
        Integer,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# =====================================================
# AUDIT EVENTS
# =====================================================

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


# =====================================================
# MEMORY HISTORY
# =====================================================

class MemoryHistory(Base):
    __tablename__ = "memory_history"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    memory_id = Column(
        Integer,
        nullable=False
    )

    user_id = Column(
        String,
        nullable=False
    )

    old_fact = Column(
        String,
        nullable=False
    )

    new_fact = Column(
        String,
        nullable=False
    )

    category = Column(
        String,
        nullable=False
    )

    old_version = Column(
        Integer,
        nullable=False
    )

    new_version = Column(
        Integer,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )