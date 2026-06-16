"""
Single source of truth for all dashboard metrics and KPIs.
"""

import json
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.database.models import AuditEvent, Memory, ClassificationStat
from app.security.attack_registry import SEVEN_ATTACKS
from app.evaluation.metrics import (
    compute_classification_metrics
)

def _all_events(db: Session):
    return db.query(AuditEvent).all()


def get_attack_statistics(db: Session) -> dict:
    events = _all_events(db)
    total = len(events)
    blocked = sum(1 for e in events if e.decision == "BLOCK")
    allowed = sum(1 for e in events if e.decision == "ALLOW")
    warning = sum(1 for e in events if e.final_decision == "ALLOW_WITH_WARNING")
    threats = sum(1 for e in events if e.threat not in ("SAFE", "NONE", None, ""))

    attack_counts = {a: 0 for a in SEVEN_ATTACKS}
    for e in events:
        at = getattr(e, "attack_type", "SAFE") or "SAFE"
        if at in attack_counts:
            attack_counts[at] += 1
        elif at == "TOOL_MANIPULATION":
            attack_counts["TOOL_POLICY_MANIPULATION"] += 1

    hitl_approved = sum(
        1 for e in events
        if isinstance(json.loads(e.explanation or "{}"), dict)
        and json.loads(e.explanation or "{}").get("human_decision") == "APPROVED"
    ) if events else 0

    hitl_rejected = sum(
        1 for e in events
        if isinstance(json.loads(e.explanation or "{}"), dict)
        and json.loads(e.explanation or "{}").get("human_decision") == "REJECTED"
    ) if events else 0

    avg_risk = sum(e.risk_score for e in events) / total if total else 0
    avg_exec = sum(getattr(e, "execution_time_ms", 0) or 0 for e in events) / total if total else 0

    attack_attempts = sum(1 for e in events if getattr(e, "attack_type", "SAFE") not in ("SAFE", "NONE", None))
    successful = sum(
        1 for e in events
        if getattr(e, "attack_type", "SAFE") not in ("SAFE", "NONE", None)
        and e.decision == "ALLOW"
    )

    return {
        "total_events": total,
        "total_requests": total,
        "blocked_events": blocked,
        "blocked": blocked,
        "allowed_events": allowed,
        "allowed": allowed,
        "allow_with_warning": warning,
        "threat_events": threats,
        "block_rate": round(blocked / total * 100, 2) if total else 0,
        "threat_rate": round(threats / total * 100, 2) if total else 0,
        "average_risk_score": round(avg_risk, 4),
        "general_chat": sum(1 for e in events if e.operation == "GENERAL_CHAT"),
        "memory_reads": sum(1 for e in events if e.operation == "READ"),
        "memory_writes": sum(1 for e in events if e.operation == "WRITE"),
        "human_approved": hitl_approved,
        "human_rejected": hitl_rejected,
        "prompt_injections": attack_counts["PROMPT_INJECTION"],
        "memory_poisoning": attack_counts["MEMORY_POISONING"],
        "false_fact_injections": attack_counts["FALSE_FACT_INJECTION"],
        "attack_success_rate": round(successful / attack_attempts, 4) if attack_attempts else 0,
        "attack_attempts": attack_attempts,
        "successful_attacks": successful,
        "seven_attack_counts": attack_counts,
        "avg_response_time_ms": round(avg_exec, 2),
        **get_extended_metrics(db),
    }


def get_extended_metrics(db: Session) -> dict:
    events = _all_events(db)
    memories = db.query(Memory).filter(Memory.active == True).all()
    stats = db.query(ClassificationStat).all()

    total = len(events) or 1
    blocked = sum(1 for e in events if e.decision == "BLOCK")
    attack_attempts = sum(
        1 for e in events
        if getattr(e, "attack_type", "SAFE") not in ("SAFE", "NONE", None)
    )
    fp = sum(1 for s in stats if s.is_false_positive)
    fn = sum(1 for s in stats if s.is_false_negative)
    stat_total = len(stats) or 1

    trust_scores = [m.trust_score for m in memories if m.trust_score is not None]
    avg_trust = sum(trust_scores) / len(trust_scores) if trust_scores else 0

    hitl_events = [
        e for e in events
        if e.final_decision == "ALLOW_WITH_WARNING"
    ]
    research_metrics = (
    compute_classification_metrics(db)
)

    return {
        "memory_accuracy": round(
            sum(1 for m in memories if m.verified) / (len(memories) or 1), 4
        ),
        "memory_retention_rate": round(
            sum(1 for m in memories if m.active) / (len(memories) or 1), 4
        ),
        "trust_score_average": round(avg_trust, 4),
        "average_trust_score": round(avg_trust, 4),
        "false_positive_rate": round(fp / stat_total, 4),
        "false_negative_rate": round(fn / stat_total, 4),
        "blocked_attack_rate": round(blocked / total, 4),
        "human_approval_rate": round(len(hitl_events) / total, 4),
        "human_rejection_rate": round(
            sum(1 for e in events if e.decision == "BLOCK") / total, 4
        ),
        "memory_conflict_rate": round(
            sum(1 for m in memories if (m.conflict_count or 0) > 0) / (len(memories) or 1), 4
        ),
        "memory_drift_rate": round(
            sum(1 for m in memories if (m.preference_drift_score or 0) > 0.5) / (len(memories) or 1), 4
        ),
        "poison_detection_accuracy": round(
            sum(1 for e in events if getattr(e, "poison_detected", False)) / total, 4
        ),
        "threat_detection_accuracy": round(
            sum(1 for e in events if e.threat not in ("SAFE", "NONE", None, "")) / total, 4
        ),
        "security_confidence": round(
            sum(getattr(e, "security_confidence", 0) or 0 for e in events) / total, 4
        ),
        "memory_confidence": round(
            sum(getattr(e, "memory_confidence", 0) or 0 for e in events) / total, 4
        ),
        "defense_effectiveness": round(
            1.0 - (sum(
                1 for e in events
                if getattr(e, "attack_type", "SAFE") not in ("SAFE", "NONE", None)
                and e.decision == "ALLOW"
            ) / (attack_attempts or 1)), 4
        ),
        "poisoning_success_rate":
research_metrics["poisoning_success_rate"],

"detection_rate":
research_metrics["detection_rate"],

"memory_contamination_rate":
research_metrics["memory_contamination_rate"],

"recovery_rate":
research_metrics["recovery_rate"],

"attack_classification_accuracy":
research_metrics["attack_classification_accuracy"],
    }


def get_memory_usage_distribution(db: Session) -> dict:
    memories = db.query(Memory).filter(Memory.active == True).all()
    counts = {"EPISODIC": 0, "SHORT_TERM": 0, "LONG_TERM": 0}
    category_counts = {}

    for m in memories:
        mtype = getattr(m, "memory_type", None) or "LONG_TERM"
        if mtype in counts:
            counts[mtype] += 1
        cat = m.category or "GENERAL"
        category_counts[cat] = category_counts.get(cat, 0) + 1

    total = sum(counts.values()) or 1
    array_form = [
        {
            "memory_type": k,
            "count": v,
            "percentage": round(v / total * 100, 2),
        }
        for k, v in counts.items()
    ]
    return {
        "array": array_form,
        "episodic": counts["EPISODIC"],
        "shortTerm": counts["SHORT_TERM"],
        "longTerm": counts["LONG_TERM"],
        "category_distribution": [
            {"category": k, "count": v, "percentage": round(v / total * 100, 2)}
            for k, v in sorted(category_counts.items(), key=lambda x: -x[1])
        ],
    }


def get_human_approval_vs_rejection(db: Session) -> dict:
    from app.database.models import QuarantineMemory

    approved = db.query(QuarantineMemory).filter(
        QuarantineMemory.review_status == "APPROVED"
    ).count()
    rejected = db.query(QuarantineMemory).filter(
        QuarantineMemory.review_status == "REJECTED"
    ).count()

    events = _all_events(db)
    warning = sum(1 for e in events if e.final_decision == "ALLOW_WITH_WARNING")
    blocked = sum(1 for e in events if e.decision == "BLOCK")

    approved = max(approved, warning)
    rejected = max(rejected, blocked)
    total = approved + rejected or 1

    return {
        "approved": approved,
        "rejected": rejected,
        "array": [
            {"action": "Approved", "count": approved, "percentage": round(approved / total * 100, 2)},
            {"action": "Rejected", "count": rejected, "percentage": round(rejected / total * 100, 2)},
        ],
    }


def get_attack_severity_breakdown(db: Session) -> dict:
    events = _all_events(db)
    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}

    for event in events:
        if event.threat in ("SAFE", "NONE", None, ""):
            continue
        risk = event.risk_score
        if risk >= 0.8:
            counts["critical"] += 1
        elif risk >= 0.6:
            counts["high"] += 1
        elif risk >= 0.3:
            counts["medium"] += 1
        else:
            counts["low"] += 1

    total = sum(counts.values()) or 1
    return {
        **counts,
        "array": [
            {"severity": k.upper(), "count": v, "percentage": round(v / total * 100, 2)}
            for k, v in counts.items()
        ],
    }


def get_trust_score_distribution(db: Session) -> list:
    memories = db.query(Memory).filter(Memory.active == True).all()
    buckets = {"0.0-0.3": 0, "0.3-0.5": 0, "0.5-0.7": 0, "0.7-0.9": 0, "0.9-1.0": 0}
    for m in memories:
        t = m.trust_score or 0.5
        if t < 0.3:
            buckets["0.0-0.3"] += 1
        elif t < 0.5:
            buckets["0.3-0.5"] += 1
        elif t < 0.7:
            buckets["0.5-0.7"] += 1
        elif t < 0.9:
            buckets["0.7-0.9"] += 1
        else:
            buckets["0.9-1.0"] += 1
    return [{"range": k, "count": v} for k, v in buckets.items()]


def get_attack_success_rate_history(db: Session) -> list:
    events = (
        db.query(AuditEvent)
        .order_by(AuditEvent.created_at.asc())
        .all()
    )
    history = []
    attempts = 0
    successes = 0
    for e in events:
        at = getattr(e, "attack_type", "SAFE") or "SAFE"
        if at in ("SAFE", "NONE"):
            continue
        attempts += 1
        if e.decision == "ALLOW":
            successes += 1
        history.append({
            "timestamp": e.created_at.isoformat() if e.created_at else "",
            "attack_success_rate": round(successes / attempts, 4) if attempts else 0,
            "attempts": attempts,
            "successes": successes,
        })
    return history


def get_full_dashboard(db: Session) -> dict:
    from app.audit.dashboard import (
        get_attack_trend_over_time,
        get_decision_distribution,
        get_threat_category_distribution,
        get_ip_intelligence,
    )

    mem = get_memory_usage_distribution(db)
    severity = get_attack_severity_breakdown(db)
    human = get_human_approval_vs_rejection(db)

    return {
        "statistics": get_attack_statistics(db),
        "attack_trend": get_attack_trend_over_time(db),
        "decision_distribution": get_decision_distribution(db),
        "threat_category_distribution": get_threat_category_distribution(db),
        "memory_usage": mem,
        "human_approval": human,
        "severity_breakdown": severity,
        "trust_distribution": get_trust_score_distribution(db),
        "attack_success_rate_history": get_attack_success_rate_history(db),
        "ip_intelligence": get_ip_intelligence(db),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
