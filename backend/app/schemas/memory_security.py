from pydantic import BaseModel
from typing import Optional


class SecurityScores(BaseModel):
    trust_score: float
    confidence_score: float
    conflict_score: float
    poison_score: float


class ValidationDecision(BaseModel):
    decision: str
    reason: str


class QuarantineRequest(BaseModel):
    user_id: str
    fact: str
    category: str
    attack_type: str
    reason: str
    risk_score: float
    poison_score: float


class PoisonEventCreate(BaseModel):
    memory_id: Optional[int] = None
    attack_type: str
    poison_score: float
    decision: str
    details: str


class PreferenceEventCreate(BaseModel):
    user_id: str
    memory_id: Optional[int] = None
    old_fact: str
    new_fact: str
    category: str = "PREFERENCE"
    stability_score: float = 1.0
    drift_score: float = 0.0
    is_legitimate_update: bool = True
    attack_type: str = "PREFERENCE_UPDATE"


class ToolPolicyEventCreate(BaseModel):
    user_id: str
    memory_id: Optional[int] = None
    policy_text: str
    violation_reason: str = ""
    risk_score: float = 0.0
    decision: str
    unapproved_domains: str = ""


class PropagationRequest(BaseModel):
    memory_id: int
    origin_agent: str
    target_agent: str
    total_agents: int = 5


class PropagationEventCreate(BaseModel):
    memory_id: int
    origin_agent: str
    target_agent: str
    propagation_path: str
    spread_score: float = 0.0
    fact: str = ""
    poison_score: float = 0.0
    attack_type: str = "NONE"
    spread_percentage: float = 0.0
    decision: str = "ALLOW"
    root_memory_id: Optional[int] = None