from sqlalchemy import func

from app.database.models import (
    AuditEvent,
    Memory,
    PreferenceEvent,
    ToolPolicyEvent,
    PropagationEvent,
)


def get_blocked_events(

    db
):

    return (

        db.query(

            AuditEvent

        )

        .filter(

            AuditEvent.decision

            ==

            "BLOCK"

        )

        .count()

    )


def get_threat_events(

    db
):

    return (

        db.query(

            AuditEvent

        )

        .filter(

            AuditEvent.threat

            !=

            "NONE"

        )

        .count()

    )


def get_conflict_events(

    db
):

    return (

        db.query(

            Memory

        )

        .filter(

            Memory.memory_version

            >

            1

        )

        .count()

    )


def get_trust_analytics(

    db
):

    value = (

        db.query(

            func.avg(

                Memory.trust_score

            )

        )

        .scalar()

    )

    if value is None:

        return 0

    return round(

        value,

        4

    )


def get_top_attack_types(

    db
):

    password = (

        db.query(

            AuditEvent

        )

        .filter(

            AuditEvent.threat

            ==

            "PASSWORD"

        )

        .count()

    )

    prompt = (

        db.query(

            AuditEvent

        )

        .filter(

            AuditEvent.threat

            ==

            "PROMPT_INJECTION"

        )

        .count()

    )

    secret = (

        db.query(

            AuditEvent

        )

        .filter(

            AuditEvent.threat

            ==

            "SECRET_RETRIEVAL"

        )

        .count()

    )

    return {

        "password":

            password,

        "prompt_injection":

            prompt,

        "secret_retrieval":

            secret

    }


def get_risk_distribution(

    db
):

    events = (

        db.query(

            AuditEvent

        )

        .all()

    )

    low = 0

    medium = 0

    high = 0

    critical = 0

    for event in events:

        score = event.risk_score

        if score < 0.25:

            low += 1

        elif score < 0.50:

            medium += 1

        elif score < 0.75:

            high += 1

        else:

            critical += 1

    return {

        "low":

            low,

        "medium":

            medium,

        "high":

            high,

        "critical":

            critical

    }


def get_attack_statistics(

    db
):

    return {

        "general_chat":

            db.query(

                AuditEvent

            )

            .filter(

                AuditEvent.operation

                ==

                "GENERAL_CHAT"

            )

            .count(),

        "memory_reads":

            db.query(

                AuditEvent

            )

            .filter(

                AuditEvent.operation

                ==

                "READ"

            )

            .count(),

        "memory_writes":

            db.query(

                AuditEvent

            )

            .filter(

                AuditEvent.operation

                ==

                "WRITE"

            )

            .count(),

        "blocked":

            db.query(

                AuditEvent

            )

            .filter(

                AuditEvent.decision

                ==

                "BLOCK"

            )

            .count(),

        "password_attacks":

            db.query(

                AuditEvent

            )

            .filter(

                AuditEvent.threat

                ==

                "PASSWORD"

            )

            .count(),

        "prompt_injections":

            db.query(

                AuditEvent

            )

            .filter(

                AuditEvent.threat

                ==

                "PROMPT_INJECTION"

            )

            .count(),

        "secret_retrievals":

            db.query(

                AuditEvent

            )

            .filter(

                AuditEvent.threat

                ==

                "SECRET_RETRIEVAL"

            )

            .count()

        }


def get_security_timeline(

    db
):

    events = (

        db.query(

            AuditEvent

        )

        .order_by(

            AuditEvent.id.desc()

        )

        .limit(

            50

        )

        .all()

    )

    result = []

    for event in events:

        label = event.operation

        if event.decision == "BLOCK":

            if event.threat == "PASSWORD":

                label = "PASSWORD BLOCKED"

            elif event.threat == "PROMPT_INJECTION":

                label = "PROMPT INJECTION"

            elif event.threat == "SECRET_RETRIEVAL":

                label = "SECRET RETRIEVAL"

            else:

                label = "SECURITY BLOCK"

        elif event.operation == "WRITE":

            label = "MEMORY WRITE"

        elif event.operation == "READ":

            label = "MEMORY READ"

        elif event.operation == "GENERAL_CHAT":

            label = "GENERAL CHAT"

        result.append(

            {

                "time":

                    event.created_at.strftime(

                        "%H:%M:%S"

                    ),

                "event":

                    label,

                "message":

                    event.payload

            }

        )

    return result


def get_attack_simulator(

    db
):

    password = (

        db.query(

            AuditEvent

        )

        .filter(

            AuditEvent.threat

            ==

            "PASSWORD"

        )

        .count()

    )

    prompt = (

        db.query(

            AuditEvent

        )

        .filter(

            AuditEvent.threat

            ==

            "PROMPT_INJECTION"

        )

        .count()

    )

    secret = (

        db.query(

            AuditEvent

        )

        .filter(

            AuditEvent.threat

            ==

            "SECRET_RETRIEVAL"

        )

        .count()

    )

    blocked = (

        db.query(

            AuditEvent

        )

        .filter(

            AuditEvent.decision

            ==

            "BLOCK"

        )

        .count()

    )

    poisoning = (

        db.query(

            AuditEvent

        )

        .filter(

            AuditEvent.threat

            ==

            "MEMORY_POISONING"

        )

        .count()

    )

    return {

        "password_attacks":

            password,

        "prompt_injections":

            prompt,

        "secret_retrievals":

            secret,

        "memory_poisoning":

            poisoning,

        "blocked_requests":

            blocked

    }


def get_trust_breakdown(

    db
):

    memories = (

        db.query(

            Memory

        )

        .all()

    )

    if not memories:

        return {

            "average":

                0,

            "minimum":

                0,

            "maximum":

                0

        }

    scores = [

        memory.trust_score

        for memory

        in memories

    ]

    return {

        "average":

            round(

                sum(scores)

                /

                len(scores),

                4

            ),

        "minimum":

            round(

                min(scores),

                4

            ),

        "maximum":

            round(

                max(scores),

                4

            )

    }


def get_user_risk_profile(

    db
):

    total_events = (

        db.query(

            AuditEvent

        )

        .count()

    )

    blocked = (

        db.query(

            AuditEvent

        )

        .filter(

            AuditEvent.decision

            ==

            "BLOCK"

        )

        .count()

    )

    password = (

        db.query(

            AuditEvent

        )

        .filter(

            AuditEvent.threat

            ==

            "PASSWORD"

        )

        .count()

    )

    prompt = (

        db.query(

            AuditEvent

        )

        .filter(

            AuditEvent.threat

            ==

            "PROMPT_INJECTION"

        )

        .count()

    )

    secret = (

        db.query(

            AuditEvent

        )

        .filter(

            AuditEvent.threat

            ==

            "SECRET_RETRIEVAL"

        )

        .count()

    )

    poison = (

        db.query(

            AuditEvent

        )

        .filter(

            AuditEvent.threat

            ==

            "MEMORY_POISONING"

        )

        .count()

    )

    attacks = (

        password

        +

        prompt

        +

        secret

        +

        poison

    )

    trust = 1.0

    trust -= blocked * 0.10

    trust -= attacks * 0.05

    if trust < 0:

        trust = 0

    if trust >= 0.80:

        risk = "LOW"

        status = "TRUSTED"

    elif trust >= 0.60:

        risk = "MEDIUM"

        status = "UNDER OBSERVATION"

    elif trust >= 0.40:

        risk = "HIGH"

        status = "SUSPICIOUS"

    else:

        risk = "CRITICAL"

        status = "HIGH RISK"

    return {

        "trust_score":

            round(

                trust,

                4

            ),

        "risk_level":

            risk,

        "blocked_requests":

            blocked,

        "attack_attempts":

            attacks,

        "status":

            status,

        "total_events":

            total_events

    }


def get_preference_drift_analytics(

    db
):

    events = (

        db.query(PreferenceEvent)

        .all()

    )

    if not events:

        return {

            "total_updates": 0,

            "legitimate_updates": 0,

            "manipulation_attempts": 0,

            "average_drift_score": 0.0,

            "average_stability_score": 1.0,

        }

    legitimate = sum(

        1

        for event in events

        if event.is_legitimate_update

    )

    manipulation = sum(

        1

        for event in events

        if event.attack_type

        ==

        "PREFERENCE_MANIPULATION"

    )

    drift_scores = [

        event.drift_score

        for event in events

    ]

    stability_scores = [

        event.stability_score

        for event in events

    ]

    return {

        "total_updates": len(events),

        "legitimate_updates": legitimate,

        "manipulation_attempts": manipulation,

        "average_drift_score": round(

            sum(drift_scores)

            /

            len(drift_scores),

            4

        ),

        "average_stability_score": round(

            sum(stability_scores)

            /

            len(stability_scores),

            4

        ),

    }


def get_preference_timeline(

    db,

    limit=50

):

    events = (

        db.query(PreferenceEvent)

        .order_by(

            PreferenceEvent.id.desc()

        )

        .limit(limit)

        .all()

    )

    return [

        {

            "id": event.id,

            "time": event.created_at.strftime(

                "%Y-%m-%d %H:%M:%S"

            ),

            "old_fact": event.old_fact,

            "new_fact": event.new_fact,

            "category": event.category,

            "stability_score": round(

                event.stability_score,

                4

            ),

            "drift_score": round(

                event.drift_score,

                4

            ),

            "is_legitimate_update":

                event.is_legitimate_update,

            "attack_type":

                event.attack_type,

        }

        for event in events

    ]


def get_preference_drift_distribution(

    db
):

    memories = (

        db.query(Memory)

        .filter(

            Memory.category

            ==

            "PREFERENCE",

            Memory.preference_drift_score.isnot(

                None

            )

        )

        .all()

    )

    low = 0

    medium = 0

    high = 0

    for memory in memories:

        score = memory.preference_drift_score

        if score < 0.33:

            low += 1

        elif score < 0.66:

            medium += 1

        else:

            high += 1

    return {

        "low": low,

        "medium": medium,

        "high": high,

    }


def get_tool_policy_violations(

    db
):

    events = (

        db.query(ToolPolicyEvent)

        .filter(

            ToolPolicyEvent.decision

            ==

            "BLOCK"

        )

        .count()

    )

    return events


def get_tool_policy_analytics(

    db
):

    events = (

        db.query(ToolPolicyEvent)

        .all()

    )

    if not events:

        return {

            "total_policies_evaluated": 0,

            "blocked_policies": 0,

            "average_risk_score": 0.0,

            "unapproved_domain_violations": 0,

            "bypass_verification_violations": 0,

        }

    blocked = sum(

        1

        for event in events

        if event.decision == "BLOCK"

    )

    domain_violations = sum(

        1

        for event in events

        if event.violation_reason.startswith(

            "UNAPPROVED_DOMAIN"

        )

    )

    bypass_violations = sum(

        1

        for event in events

        if event.violation_reason

        ==

        "BYPASS_VERIFICATION"

    )

    risk_scores = [

        event.risk_score

        for event in events

    ]

    return {

        "total_policies_evaluated": len(events),

        "blocked_policies": blocked,

        "average_risk_score": round(

            sum(risk_scores)

            /

            len(risk_scores),

            4

        ),

        "unapproved_domain_violations":

            domain_violations,

        "bypass_verification_violations":

            bypass_violations,

    }


def get_tool_policy_timeline(

    db,

    limit=50

):

    events = (

        db.query(ToolPolicyEvent)

        .order_by(

            ToolPolicyEvent.id.desc()

        )

        .limit(limit)

        .all()

    )

    return [

        {

            "id": event.id,

            "time": event.created_at.strftime(

                "%Y-%m-%d %H:%M:%S"

            ),

            "policy_text": event.policy_text,

            "violation_reason":

                event.violation_reason,

            "risk_score": round(

                event.risk_score,

                4

            ),

            "decision": event.decision,

            "unapproved_domains":

                event.unapproved_domains,

        }

        for event in events

    ]


def get_propagation_analytics(

    db
):

    events = (

        db.query(PropagationEvent)

        .all()

    )

    if not events:

        return {

            "total_propagations": 0,

            "blocked_propagations": 0,

            "successful_propagations": 0,

            "average_spread_rate": 0.0,

            "average_spread_percentage": 0.0,

            "max_spread_percentage": 0.0,

        }

    blocked = sum(

        1

        for event in events

        if event.decision == "BLOCK"

    )

    allowed = sum(

        1

        for event in events

        if event.decision == "ALLOW"

    )

    spread_rates = [

        event.spread_score

        for event in events

    ]

    spread_percentages = [

        event.spread_percentage

        for event in events

    ]

    return {

        "total_propagations": len(events),

        "blocked_propagations": blocked,

        "successful_propagations": allowed,

        "average_spread_rate": round(

            sum(spread_rates)

            /

            len(spread_rates),

            4

        ),

        "average_spread_percentage": round(

            sum(spread_percentages)

            /

            len(spread_percentages),

            2

        ),

        "max_spread_percentage": round(

            max(spread_percentages),

            2

        ),

    }


def get_propagation_timeline(

    db,

    limit=50
):

    events = (

        db.query(PropagationEvent)

        .order_by(

            PropagationEvent.id.desc()

        )

        .limit(limit)

        .all()

    )

    return [

        {

            "id": event.id,

            "time": event.created_at.strftime(

                "%Y-%m-%d %H:%M:%S"

            ),

            "origin_agent":

                event.origin_agent,

            "target_agent":

                event.target_agent,

            "propagation_path":

                event.propagation_path,

            "spread_score": round(

                event.spread_score,

                4

            ),

            "spread_percentage": round(

                event.spread_percentage,

                2

            ),

            "poison_score": round(

                event.poison_score,

                4

            ),

            "attack_type":

                event.attack_type,

            "decision":

                event.decision,

            "fact": event.fact,

            "root_memory_id":

                event.root_memory_id,

        }

        for event in events

    ]


def get_propagation_attack_count(

    db
):

    return (

        db.query(PropagationEvent)

        .filter(

            PropagationEvent.attack_type

            ==

            "PROPAGATION_ATTACK"

        )

        .count()

    )


def get_attack_statistics(db):
    return {
        "totalRequests": db.query(AuditEvent).count(),
        "allowedRequests": db.query(AuditEvent).filter(AuditEvent.final_decision == "ALLOW").count(),
        "blockedAttacks": db.query(AuditEvent).filter(AuditEvent.final_decision == "BLOCK").count(),
        "allowWithWarning": db.query(AuditEvent).filter(AuditEvent.final_decision == "ALLOW_WITH_WARNING").count(),
        "humanApproved": db.query(AuditEvent).filter(AuditEvent.explanation.like('%"human_decision":"APPROVED"%')).count(),
        "humanRejected": db.query(AuditEvent).filter(AuditEvent.explanation.like('%"human_decision":"REJECTED"%')).count(),
        "promptInjectionAttempts": db.query(AuditEvent).filter(AuditEvent.attack_type == "PROMPT_INJECTION").count(),
        "memoryPoisoningAttempts": db.query(AuditEvent).filter(AuditEvent.attack_type == "MEMORY_POISONING").count(),
        "falseFactInjectionAttempts": db.query(AuditEvent).filter(AuditEvent.attack_type == "FALSE_FACT_INJECTION").count()
    }


def get_attack_trend_over_time(db):
    # Return last 24 hours of data, grouped by hour
    from datetime import datetime, timedelta
    # This is a simplified implementation - in production you'd want proper time-series aggregation
    twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
    events = db.query(AuditEvent).filter(AuditEvent.created_at >= twenty_four_hours_ago).all()

    # Group by hour
    hourly_counts = {}
    for event in events:
        hour_key = event.created_at.strftime("%Y-%m-%d %H:00")
        hourly_counts[hour_key] = hourly_counts.get(hour_key, 0) + 1

    # Convert to list of {time, count} objects sorted by time
    result = [{"time": time, "count": count} for time, count in sorted(hourly_counts.items())]
    return result


def get_decision_distribution(db):
    allowed = db.query(AuditEvent).filter(AuditEvent.final_decision == "ALLOW").count()
    blocked = db.query(AuditEvent).filter(AuditEvent.final_decision == "BLOCK").count()
    allow_with_warning = db.query(AuditEvent).filter(AuditEvent.final_decision == "ALLOW_WITH_WARNING").count()

    return {
        "allowed": allowed,
        "blocked": blocked,
        "allowWithWarning": allow_with_warning
    }


def get_threat_category_distribution(db):
    # Get threat types and their counts
    threat_types = db.query(AuditEvent.threat).distinct().all()
    result = []
    for (threat_type,) in threat_types:
        if threat_type and threat_type != "NONE":
            count = db.query(AuditEvent).filter(AuditEvent.threat == threat_type).count()
            result.append({"category": threat_type, "count": count})
    return result


def get_memory_usage_distribution(db):
    # This is a simplified implementation
    total_memories = db.query(Memory).count()
    if total_memories == 0:
        return {"episodic": 0, "shortTerm": 0, "longTerm": 0}

    episodic = db.query(Memory).filter(
        (Memory.category == "EPISODIC") | (Memory.source.like("%session%"))
    ).count()

    short_term = db.query(Memory).filter(
        (Memory.category == "SHORT_TERM") | (Memory.importance_score < 0.5)
    ).count()

    long_term = db.query(Memory).filter(
        (Memory.category == "LONG_TERM") |
        ((Memory.trust_score > 0.7) & (Memory.importance_score >= 0.5))
    ).count()

    # Calculate percentages
    episodic_pct = round((episodic / total_memories) * 100) if total_memories > 0 else 0
    short_term_pct = round((short_term / total_memories) * 100) if total_memories > 0 else 0
    long_term_pct = round((long_term / total_memories) * 100) if total_memories > 0 else 0

    return {
        "episodic": episodic_pct,
        "shortTerm": short_term_pct,
        "longTerm": long_term_pct
    }


def get_human_approval_vs_rejection(db):
    approved = db.query(AuditEvent).filter(AuditEvent.explanation.like('%"human_decision":"APPROVED"%')).count()
    rejected = db.query(AuditEvent).filter(AuditEvent.explanation.like('%"human_decision":"REJECTED"%')).count()

    return {
        "approved": approved,
        "rejected": rejected
    }


def get_attack_severity_breakdown(db):
    # Count by risk level
    high_risk = db.query(AuditEvent).filter(AuditEvent.risk_level == "HIGH").count()
    medium_risk = db.query(AuditEvent).filter(AuditEvent.risk_level == "MEDIUM").count()
    low_risk = db.query(AuditEvent).filter(AuditEvent.risk_level == "LOW").count()
    critical_risk = db.query(AuditEvent).filter(AuditEvent.risk_level == "CRITICAL").count()

    return {
        "severityLevels": [
            {"level": "LOW", "count": low_risk},
            {"level": "MEDIUM", "count": medium_risk},
            {"level": "HIGH", "count": high_risk},
            {"level": "CRITICAL", "count": critical_risk}
        ]
    }


def get_ip_intelligence(db):
    # Get unique IPs and their info
    # This is a simplified implementation
    ip_records = db.query(AuditEvent).filter(AuditEvent.explanation.isnot(None)).all()

    # Extract IP addresses from explanation (this would be more robust in a real implementation)
    ip_data = []
    seen_ips = set()

    for record in ip_records:
        # Very basic IP extraction - in reality you'd store IP separately
        explanation_str = str(record.explanation)
        # This is a placeholder - you'd have a proper IP tracking system
        if len(ip_data) < 10:  # Limit for demo
            ip_data.append({
                "ipAddress": f"192.168.1.{len(ip_data)+1}",
                "country": "Unknown",
                "riskScore": len(ip_data) * 10
            })

    return ip_data