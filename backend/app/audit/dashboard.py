from sqlalchemy import func

from app.database.models import (
    AuditEvent,
    Memory
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

            Memory.version

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