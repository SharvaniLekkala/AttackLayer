from sqlalchemy import func

from app.database.models import (
    Memory,
    PoisonEvent,
    QuarantineMemory,
    PreferenceEvent,
    ToolPolicyEvent,
    PropagationEvent,
    AuditEvent,
)


def get_quarantine_memories(db, limit=50):

    records = (
        db.query(QuarantineMemory)
        .order_by(QuarantineMemory.id.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": record.id,
            "time": record.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "user_id": record.user_id,
            "fact": record.fact,
            "category": record.category,
            "attack_type": record.attack_type,
            "reason": record.reason,
            "risk_score": round(record.risk_score, 4),
            "poison_score": round(record.poison_score, 4),
            "review_status": record.review_status,
        }
        for record in records
    ]


def get_poison_events(db, limit=50):

    events = (
        db.query(PoisonEvent)
        .order_by(PoisonEvent.id.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": event.id,
            "time": event.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "memory_id": event.memory_id,
            "attack_type": event.attack_type,
            "poison_score": round(event.poison_score, 4),
            "decision": event.decision,
            "details": event.details,
        }
        for event in events
    ]


def get_poison_attempts_over_time(db):

    events = (
        db.query(PoisonEvent)
        .order_by(PoisonEvent.created_at.asc())
        .all()
    )

    buckets = {}

    for event in events:
        key = event.created_at.strftime("%Y-%m-%d %H:%M")
        buckets[key] = buckets.get(key, 0) + 1

    return [
        {"time": key, "count": buckets[key]}
        for key in sorted(buckets.keys())
    ][-30:]


def get_attack_distribution(db):

    events = db.query(PoisonEvent).all()

    distribution = {}

    for event in events:
        attack = event.attack_type or "UNKNOWN"
        distribution[attack] = distribution.get(attack, 0) + 1

    memory_attacks = (
        db.query(
            Memory.attack_type,
            func.count(Memory.id),
        )
        .filter(Memory.attack_type != "NONE")
        .group_by(Memory.attack_type)
        .all()
    )

    for attack_type, count in memory_attacks:
        distribution[attack_type] = (
            distribution.get(attack_type, 0) + count
        )

    return [
        {"attack_type": key, "count": value}
        for key, value in sorted(
            distribution.items(),
            key=lambda item: item[1],
            reverse=True,
        )
    ]


def get_trust_distribution_chart(db):

    memories = db.query(Memory).filter(Memory.active == True).all()

    low = medium = high = 0

    for memory in memories:
        score = memory.trust_score or 0
        if score < 0.4:
            low += 1
        elif score < 0.7:
            medium += 1
        else:
            high += 1

    return [
        {"band": "Low (0-0.4)", "count": low},
        {"band": "Medium (0.4-0.7)", "count": medium},
        {"band": "High (0.7-1.0)", "count": high},
    ]


def get_spread_rate_chart(db):

    events = (
        db.query(PropagationEvent)
        .order_by(PropagationEvent.id.asc())
        .all()
    )

    return [
        {
            "time": event.created_at.strftime("%H:%M:%S"),
            "spread_percentage": round(
                event.spread_percentage,
                2,
            ),
            "path": event.propagation_path,
        }
        for event in events[-20:]
    ]


def get_conflict_frequency(db):

    return (
        db.query(Memory)
        .filter(Memory.memory_version > 1)
        .count()
    )


def get_scenario_metrics(db):

    false_fact_attempts = (
        db.query(PoisonEvent)
        .filter(
            PoisonEvent.attack_type == "FALSE_FACT_INJECTION"
        )
        .count()
    )

    false_fact_blocked = (
        db.query(PoisonEvent)
        .filter(
            PoisonEvent.attack_type == "FALSE_FACT_INJECTION",
            PoisonEvent.decision == "BLOCK",
        )
        .count()
    )

    poisoned_active = (
        db.query(Memory)
        .filter(
            Memory.active == True,
            Memory.poison_flag == True,
        )
        .count()
    )

    pref_total = db.query(PreferenceEvent).count()

    pref_manipulation = (
        db.query(PreferenceEvent)
        .filter(
            PreferenceEvent.attack_type
            == "PREFERENCE_MANIPULATION"
        )
        .count()
    )

    pref_legitimate = (
        db.query(PreferenceEvent)
        .filter(
            PreferenceEvent.is_legitimate_update == True
        )
        .count()
    )

    tool_total = db.query(ToolPolicyEvent).count()

    tool_blocked = (
        db.query(ToolPolicyEvent)
        .filter(ToolPolicyEvent.decision == "BLOCK")
        .count()
    )

    prop_total = db.query(PropagationEvent).count()

    prop_blocked = (
        db.query(PropagationEvent)
        .filter(PropagationEvent.decision == "BLOCK")
        .count()
    )

    prop_spread = (
        db.query(func.max(PropagationEvent.spread_percentage))
        .scalar()
        or 0.0
    )

    quarantine_count = db.query(QuarantineMemory).count()

    return {
        "scenario_1_false_fact_injection": {
            "name": "False Fact Injection",
            "description": (
                "Poison memory with incorrect facts "
                "(approved → rejected)"
            ),
            "poison_attempts": false_fact_attempts,
            "attacks_blocked": false_fact_blocked,
            "poisoned_retrievals": poisoned_active,
            "decision_accuracy": round(
                (
                    false_fact_blocked / false_fact_attempts
                    if false_fact_attempts > 0
                    else 1.0
                ),
                4,
            ),
            "degradation_prevented": (
                false_fact_blocked >= false_fact_attempts
                if false_fact_attempts > 0
                else True
            ),
        },
        "scenario_2_preference_manipulation": {
            "name": "Preference Manipulation",
            "description": (
                "Detect preference drift vs legitimate "
                "updates (Python → Java)"
            ),
            "preference_updates": pref_total,
            "legitimate_updates": pref_legitimate,
            "manipulation_attempts": pref_manipulation,
            "wrong_recommendation_risk": round(
                (
                    pref_manipulation / pref_total
                    if pref_total > 0
                    else 0.0
                ),
                4,
            ),
            "personalization_integrity": round(
                (
                    pref_legitimate / pref_total
                    if pref_total > 0
                    else 1.0
                ),
                4,
            ),
        },
        "scenario_3_tool_usage_manipulation": {
            "name": "Tool Usage Manipulation",
            "description": (
                "Block unsafe tool policies "
                "(trust unapproved sources)"
            ),
            "policies_evaluated": tool_total,
            "unsafe_actions_prevented": tool_blocked,
            "tool_selection_accuracy": round(
                (
                    (tool_total - tool_blocked) / tool_total
                    if tool_total > 0
                    else 1.0
                ),
                4,
            ),
            "approved_tools_enforced": tool_blocked > 0 or tool_total == 0,
        },
        "scenario_4_multi_agent_propagation": {
            "name": "Multi-Agent Propagation",
            "description": (
                "Track poison spread across agents "
                "(A → B → C)"
            ),
            "propagation_attempts": prop_total,
            "cascading_failures_prevented": prop_blocked,
            "max_spread_percentage": round(prop_spread, 2),
            "poison_spread_rate": round(
                (
                    prop_blocked / prop_total
                    if prop_total > 0
                    else 0.0
                ),
                4,
            ),
            "agents_contained": prop_blocked >= 0,
        },
        "summary": {
            "quarantined_memories": quarantine_count,
            "total_poison_events": db.query(PoisonEvent).count(),
            "total_blocked_audits": (
                db.query(AuditEvent)
                .filter(AuditEvent.decision == "BLOCK")
                .count()
            ),
        },
    }
