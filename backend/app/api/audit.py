import json
from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.session import (
    get_db
)
from app.database.models import (
    AuditEvent
)
from app.audit.dashboard import (
    get_blocked_events,
    get_threat_events,
    get_conflict_events,
    get_trust_analytics,
    get_top_attack_types,
    get_risk_distribution,
    get_attack_statistics,
    get_security_timeline,
    get_attack_simulator,
    get_trust_breakdown,
    get_user_risk_profile,
    get_preference_drift_analytics,
    get_preference_timeline,
    get_preference_drift_distribution,
    get_tool_policy_violations,
    get_tool_policy_analytics,
    get_tool_policy_timeline,
    get_propagation_analytics,
    get_propagation_timeline,
    get_propagation_attack_count,
    get_attack_trend_over_time,
    get_decision_distribution,
    get_threat_category_distribution,
    get_memory_usage_distribution,
    get_human_approval_vs_rejection,
    get_attack_severity_breakdown,
    get_ip_intelligence
)
router = APIRouter(prefix="/audit",tags=["Audit"])

@router.get("/events")
def get_events(db: Session = Depends(get_db)):
    events = (

        db.query(
            AuditEvent
        )

        .order_by(
            AuditEvent.id.desc()
        )

        .all()

    )

    result = []

    for event in events:

        retrieved = []
        memories_used = []
        explanation = {}
        trust_scores = []

        try:
            retrieved = json.loads(event.retrieved_memories or "[]")
        except (json.JSONDecodeError, TypeError):
            pass

        try:
            memories_used = json.loads(event.memories_used or "[]")
        except (json.JSONDecodeError, TypeError):
            pass

        try:
            explanation = json.loads(event.explanation or "{}")
        except (json.JSONDecodeError, TypeError):
            pass

        try:
            trust_scores = json.loads(getattr(event, "trust_scores", "[]") or "[]")
        except (json.JSONDecodeError, TypeError):
            pass

        result.append({
            "id": event.id,
            "time": event.created_at.strftime("%H:%M:%S"),
            "prompt": event.payload,
            "operation": event.operation,
            "threat": event.threat if event.threat else "NONE",
            "risk_score": round(event.risk_score, 4),
            "decision": event.decision,
            "intent": getattr(event, "intent", "UNKNOWN") or "UNKNOWN",
            "intent_confidence": round(
                getattr(event, "intent_confidence", 0.0) or 0.0, 4
            ),
            "attack_type": getattr(event, "attack_type", "SAFE") or "SAFE",
            "attack_confidence": round(
                getattr(event, "attack_confidence", 0.0) or 0.0, 4
            ),
            "risk_level": getattr(event, "risk_level", "LOW") or "LOW",
            "memory_category": getattr(event, "memory_category", "GENERAL") or "GENERAL",
            "conflict_status": getattr(event, "conflict_status", "NONE") or "NONE",
            "trust_scores": trust_scores,
            "retrieved_memories": retrieved,
            "memories_used": memories_used,
            "poison_detected": getattr(event, "poison_detected", False) or False,
            "quarantine_status": getattr(event, "quarantine_status", "NONE") or "NONE",
            "response_confidence": round(
                getattr(event, "response_confidence", 0.0) or 0.0, 4
            ),
            "execution_time_ms": round(
                getattr(event, "execution_time_ms", 0.0) or 0.0, 2
            ),
            "final_decision": getattr(event, "final_decision", event.decision) or event.decision,
            "explanation": explanation,
        })

    return result


@router.get("/blocked")
def blocked_events(

    db: Session = Depends(
        get_db
    )

):

    return get_blocked_events(
        db
    )


@router.get("/threats")
def threat_events(

    db: Session = Depends(
        get_db
    )

):

    return get_threat_events(
        db
    )


@router.get("/conflicts")
def conflict_events(

    db: Session = Depends(
        get_db
    )

):

    return get_conflict_events(
        db
    )


@router.get("/trust")
def trust_analytics(

    db: Session = Depends(
        get_db
    )

):

    return get_trust_analytics(
        db
    )


@router.get("/top-attacks")
def top_attacks(

    db: Session = Depends(
        get_db
    )

):

    return get_top_attack_types(
        db
    )


@router.get("/risk-distribution")
def risk_distribution(

    db: Session = Depends(
        get_db
    )

):

    return get_risk_distribution(
        db
    )

@router.get("/timeline")
def security_timeline(

    db: Session = Depends(
        get_db
    )

):

    return get_security_timeline(

        db

    )
@router.get("/attack-simulator")
def attack_simulator(

    db: Session = Depends(
        get_db
    )

):

    return get_attack_simulator(

        db

    )
@router.get(
    "/trust-breakdown"
)
def trust_breakdown(

    db: Session = Depends(
        get_db
    )

):

    return get_trust_breakdown(

        db

    )
@router.get(
    "/user-risk"
)
def user_risk(

    db: Session = Depends(
        get_db
    )

):

    return get_user_risk_profile(

        db

    )


@router.get("/preference-drift")
def preference_drift_analytics(

    db: Session = Depends(
        get_db
    )

):

    return get_preference_drift_analytics(
        db
    )


@router.get("/preference-timeline")
def preference_timeline(

    db: Session = Depends(
        get_db
    )

):

    return get_preference_timeline(
        db
    )


@router.get("/preference-drift-distribution")
def preference_drift_distribution(

    db: Session = Depends(
        get_db
    )

):

    return get_preference_drift_distribution(
        db
    )


@router.get("/tool-policy-violations")
def tool_policy_violations(

    db: Session = Depends(
        get_db
    )

):

    return get_tool_policy_violations(
        db
    )


@router.get("/tool-policy-analytics")
def tool_policy_analytics(

    db: Session = Depends(
        get_db
    )

):

    return get_tool_policy_analytics(
        db
    )


@router.get("/tool-policy-timeline")
def tool_policy_timeline(

    db: Session = Depends(
        get_db
    )

):

    return get_tool_policy_timeline(
        db
    )


@router.get("/propagation-analytics")
def propagation_analytics(

    db: Session = Depends(
        get_db
    )

):

    return get_propagation_analytics(
        db
    )


@router.get("/propagation-timeline")
def propagation_timeline(

    db: Session = Depends(
        get_db
    )

):

    return get_propagation_timeline(
        db
    )


@router.get("/propagation-attacks")
def propagation_attacks(

    db: Session = Depends(
        get_db
    )

):

    return {
        "propagation_attacks":
            get_propagation_attack_count(db)
    }


@router.get("/attack-statistics")
def attack_statistics(
    db: Session = Depends(get_db)
):
    return get_attack_statistics(db)


@router.get("/attack-trend-over-time")
def attack_trend_over_time(
    db: Session = Depends(get_db)
):
    return get_attack_trend_over_time(db)


@router.get("/decision-distribution")
def decision_distribution(
    db: Session = Depends(get_db)
):
    return get_decision_distribution(db)


@router.get("/threat-category-distribution")
def threat_category_distribution(
    db: Session = Depends(get_db)
):
    return get_threat_category_distribution(db)


@router.get("/memory-usage-distribution")
def memory_usage_distribution(
    db: Session = Depends(get_db)
):
    return get_memory_usage_distribution(db)


@router.get("/human-approval-vs-rejection")
def human_approval_vs_rejection(
    db: Session = Depends(get_db)
):
    return get_human_approval_vs_rejection(db)


@router.get("/attack-severity-breakdown")
def attack_severity_breakdown(
    db: Session = Depends(get_db)
):
    return get_attack_severity_breakdown(db)


@router.get("/ip-intelligence")
def ip_intelligence(
    db: Session = Depends(get_db)
):
    return get_ip_intelligence(db)
