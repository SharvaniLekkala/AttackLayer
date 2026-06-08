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

    get_propagation_attack_count

)
router = APIRouter(

    prefix="/audit",

    tags=["Audit"]

)


@router.get("/events")
def get_events(

    db: Session = Depends(
        get_db
    )

):

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

        result.append(

            {

                "id":

                    event.id,

                "time":

                    event.created_at.strftime(

                        "%H:%M:%S"

                    ),

                "prompt":

                    event.payload,

                "operation":

                    event.operation,

                "threat":

                    event.threat

                    if

                    event.threat

                    else

                    "NONE",

                "risk_score":

                    round(

                        event.risk_score,

                        4

                    ),

                "decision":

                    event.decision

            }

        )

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
@router.get("/attack-statistics")
def attack_statistics(

    db: Session = Depends(
        get_db
    )

):

    return get_attack_statistics(

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