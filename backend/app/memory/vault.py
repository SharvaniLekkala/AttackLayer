from sqlalchemy.orm import Session

from app.database.models import (
    Memory,
    MemoryHistory
)

from app.memory.embedding_service import (
    generate_embedding
)

from app.memory.vector_storage import (
    add_memory_embedding,
    remove_memory_embedding
)

from app.security.security_gateway import (
    evaluate_security
)

from app.security.memory_conflict_engine import (
    detect_conflict
)

from app.security.trust_engine import (
    calculate_trust
)

from app.audit.history_logger import (
    log_memory_history
)

from app.memory_security.services.memory_security_pipeline import (
    MemorySecurityPipeline
)

from app.memory_security.quarantine.quarantine_manager import (
    quarantine_memory
)
from app.memory_security.services.poison_event_logger import (
    log_poison_event
)

from app.memory_security.services.preference_event_logger import (
    log_preference_event
)

from app.memory_security.services.tool_policy_event_logger import (
    log_tool_policy_event
)

def create_memory(
    db,
    user_id,
    fact
):

    security_result = evaluate_security(
        fact
    )

    if security_result["decision"] == "BLOCK":

        attack_type = (
            security_result.get(
                "tool_policy_type"
            )
            or security_result.get(
                "memory_poison_type"
            )
            or security_result.get(
                "threat"
            )
            or "Security Policy"
        )

        if security_result.get(
            "tool_policy_type"
        ):

            log_tool_policy_event(

                db=db,

                user_id=user_id,

                policy_text=fact,

                violation_reason=(
                    security_result.get(
                        "tool_policy_violation"
                    )
                    or ""
                ),

                risk_score=(
                    security_result.get(
                        "risk_score",
                        0.0
                    )
                ),

                decision="BLOCK",

                unapproved_domains=",".join(
                    security_result.get(
                        "tool_policy_unapproved_domains",
                        []
                    )
                ),

            )

            log_poison_event(

                db=db,

                attack_type=attack_type,

                poison_score=(
                    security_result.get(
                        "risk_score",
                        0.9
                    )
                ),

                decision="BLOCK",

                details=fact

            )

        return {

            "status": "blocked",

            "attack_type": attack_type,

            "security": security_result
        }

    conflict_result = detect_conflict(

        db=db,

        user_id=user_id,

        fact=fact,

        category=security_result["category"]

    )

    new_version = 1

    conflict_detected = False

    existing_memory = None

    conflict_score = 0.0

    poison_score = 0.0

    attack_type = "NONE"

    drift_score = None

    stability_score = None

    if conflict_result:

        conflict_detected = True

        existing_memory = conflict_result["memory"]

        conflict_score = conflict_result.get(
            "conflict_score",
            0.0
        )

        poison_score = conflict_result.get(
            "poison_score",
            0.0
        )

        attack_type = conflict_result.get(
            "attack_type",
            "SAFE"
        )

        drift_score = conflict_result.get(
            "drift_score"
        )

        stability_score = conflict_result.get(
            "stability_score"
        )

        # ===================================
        # Duplicate Memory
        # ===================================

        if attack_type == "DUPLICATE":
            existing_memory.verification_count = (
                (existing_memory.verification_count or 0) + 1
            )
            db.commit()

            return {
                "status": "duplicate",
                "memory_id": existing_memory.id,
                "memory_version": existing_memory.memory_version,
                "attack_type": "DUPLICATE",
                "decision": "ALLOW"
            }

        new_version = (
            existing_memory.memory_version
            + 1
        )
    
    # ===================================
    # Preserve memory lineage
    # ===================================

    parent_memory_id = None

    if existing_memory:

        parent_memory_id = existing_memory.id
    trust_result = calculate_trust(

        source="USER",

        security_decision=
            security_result["decision"],

        category_confidence=
            security_result["category_confidence"],

        conflict_detected=
            conflict_detected,

        version=new_version,

        attack_type=attack_type

    )

    # ===================================
    # Override detector values
    # ===================================

    trust_result["conflict_score"] = max(
        trust_result["conflict_score"],
        conflict_score
    )

    trust_result["poison_score"] = max(
        trust_result["poison_score"],
        poison_score
    )

    pipeline_result = (

        MemorySecurityPipeline.evaluate(

            trust_score=
                trust_result[
                    "trust_score"
                ],

            confidence_score=
                trust_result[
                    "confidence_score"
                ],

            conflict_score=
                trust_result[
                    "conflict_score"
                ],

            poison_score=
                trust_result[
                    "poison_score"
                ]
        )

    )

    final_decision = (
        pipeline_result[
            "decision"
        ]
    )
    print("\n========== MEMORY DEBUG ==========")
    print("FACT:", fact)
    print("ATTACK TYPE:", attack_type)
    print("CONFLICT SCORE:", trust_result["conflict_score"])
    print("POISON SCORE:", trust_result["poison_score"])
    print("FINAL DECISION:", final_decision)
    print("==================================\n")

    # ===================================
    # QUARANTINE
    # ===================================

    if final_decision == "QUARANTINE":

        quarantine_record = (

            quarantine_memory(

                db=db,

                user_id=user_id,

                fact=fact,

                category=
                    security_result[
                        "category"
                    ],

                attack_type=
                    attack_type,

                reason=
                    "Memory poisoning review",

                risk_score=
                    security_result[
                        "risk_score"
                    ],

                poison_score=
                    trust_result[
                        "poison_score"
                    ]

            )

        )

        log_poison_event(

            db=db,

            attack_type=
                attack_type,

            poison_score=
                trust_result[
                    "poison_score"
                ],

            decision=
                final_decision,

            details=
                fact

        )

        return {

            "status":
                "quarantined",

            "quarantine_id":
                quarantine_record.id,

            "attack_type":
                attack_type,

            "decision":
                final_decision

        }

    # ===================================
    # BLOCK
    # ===================================

    if final_decision == "BLOCK":

        log_poison_event(

            db=db,

            attack_type=
                attack_type,

            poison_score=
                trust_result[
                    "poison_score"
                ],

            decision=
                final_decision,

            details=
                fact

        )

        if attack_type == "TOOL_POLICY_POISONING":

            log_tool_policy_event(

                db=db,

                user_id=user_id,

                policy_text=fact,

                violation_reason=(
                    conflict_result.get(
                        "violation_reason"
                    )
                    if conflict_result
                    else ""
                ),

                risk_score=trust_result[
                    "poison_score"
                ],

                decision=final_decision,

                unapproved_domains=",".join(
                    security_result.get(
                        "tool_policy_unapproved_domains",
                        []
                    )
                ),

                memory_id=(
                    existing_memory.id
                    if existing_memory
                    else None
                ),

            )

        return {

            "status":
                "blocked",

            "attack_type":
                attack_type,

            "decision":
                final_decision

            }

    # ===================================
    # STORE MEMORY
    # ===================================
    # ===================================
    # Archive previous version
    # ===================================

    if (
        conflict_detected
        and
        attack_type
        in (
            "NONE",
            "PREFERENCE_UPDATE",
            "TOOL_POLICY_UPDATE",
        )
        and
        existing_memory
    ):

        existing_memory.active = False
        existing_memory.status = "ARCHIVED"
        existing_memory.conflict_count = (
            (getattr(existing_memory, "conflict_count", 0) or 0) + 1
        )

        remove_memory_embedding(
            existing_memory.id
        )

        if (
            attack_type
            ==
            "PREFERENCE_UPDATE"
            and
            existing_memory
        ):

            log_preference_event(

                db=db,

                user_id=user_id,

                memory_id=existing_memory.id,

                old_fact=existing_memory.fact,

                new_fact=fact,

                category=security_result[
                    "category"
                ],

                stability_score=(
                    stability_score or 1.0
                ),

                drift_score=(
                    drift_score or 0.0
                ),

                is_legitimate_update=True,

                attack_type="PREFERENCE_UPDATE"

            )

        log_memory_history(

            db=db,

            old_memory=
                existing_memory,

            new_fact=
                fact,

            new_version=
                new_version

        )

        db.commit()
    memory = Memory(

        user_id=user_id,

        fact=fact,

        category=
            security_result[
                "category"
            ],

        trust_score=
            trust_result[
                "trust_score"
            ],

        confidence_score=
            trust_result[
                "confidence_score"
            ],

        conflict_score=
            trust_result[
                "conflict_score"
            ],

        poison_score=
            trust_result[
                "poison_score"
            ],

        risk_score=
            security_result[
                "risk_score"
            ],

        source="USER",

        attack_type=
            attack_type,

        final_decision=
            final_decision,

        poison_flag=
            trust_result[
                "poison_score"
            ] > 0.8,

        memory_version=
            new_version,
        parent_memory_id=
    parent_memory_id,

        active=True,
        status="ACTIVE",
        verification_count=1,

        preference_stability_score=
            stability_score,

        preference_drift_score=
            drift_score

    )

    db.add(memory)

    db.commit()

    db.refresh(memory)

    embedding = generate_embedding(
        fact
    )

    add_memory_embedding(

        memory.id,

        fact,

        embedding

    )

    return {

        "status":
            "stored",

        "memory_id":
            memory.id,

        "memory_version":
            memory.memory_version,

        "decision":
            final_decision,

        "attack_type":
            attack_type,

        "poison_score":
            trust_result[
                "poison_score"
            ],

        "conflict_detected":
            conflict_detected,

        "category":
            security_result["category"],

        "trust_score":
            trust_result["trust_score"],

        "security":
            security_result

    }


def get_all_memories(
    db: Session
):
    return db.query(
        Memory
    ).all()


def get_memory_by_id(
    db: Session,
    memory_id: int
):
    return (
        db.query(Memory)
        .filter(
            Memory.id == memory_id
        )
        .first()
    )


def archive_memory(
    db: Session,
    memory_id: int
):

    memory = (
        db.query(Memory)
        .filter(
            Memory.id == memory_id
        )
        .first()
    )

    if not memory:
        return None

    memory.active = False
    memory.status = "ARCHIVED"

    remove_memory_embedding(
        memory_id
    )

    db.commit()

    db.refresh(memory)

    return memory


def get_memory_history(
    db,
    memory_id
):

    return (
        db.query(
            MemoryHistory
        )
        .filter(
            MemoryHistory.memory_id
            == memory_id
        )
        .all()
    )
