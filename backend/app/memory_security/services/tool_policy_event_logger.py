from app.database.models import (
    ToolPolicyEvent
)


def log_tool_policy_event(
    db,
    user_id,
    policy_text,
    violation_reason,
    risk_score,
    decision,
    unapproved_domains="",
    memory_id=None
):

    event = ToolPolicyEvent(

        user_id=user_id,

        memory_id=memory_id,

        policy_text=policy_text,

        violation_reason=violation_reason or "",

        risk_score=risk_score,

        decision=decision,

        unapproved_domains=unapproved_domains,

    )

    db.add(event)

    db.commit()

    db.refresh(event)

    return event
