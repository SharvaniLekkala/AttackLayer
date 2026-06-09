from app.database.models import (
    Memory,
    MemoryHistory,
    PreferenceEvent,
)

from app.memory_security.detectors.false_fact_detector import (
    detect_false_fact_injection
)

from app.memory_security.detectors.preference_manipulation_detector import (
    detect_preference_update
)

from app.memory_security.detectors.tool_policy_validator import (
    ToolPolicyValidator
)

PREFERENCE_CATEGORIES = {
    "FOOD_PREFERENCE",
    "CODING_PREFERENCE",
    "SPORT_PREFERENCE",
    "PERSONAL_PREFERENCE",
}

TOOL_POLICY_CATEGORIES = {
    "TOOL_POLICY"
}

EXCLUSIVE_CATEGORIES = {
    "CODING_PREFERENCE",
    "LOCATION",
    "PROFESSION",
}


def _is_exclusive_preference(fact, category):
    lowered = fact.lower()
    return (
        category in EXCLUSIVE_CATEGORIES
        or "favorite" in lowered
        or "favourite" in lowered
        or "instead" in lowered
        or "now prefer" in lowered
    )


def _get_preference_history(
    db,
    user_id,
    category
):

    events = (

        db.query(PreferenceEvent)

        .filter(

            PreferenceEvent.user_id == user_id,

            PreferenceEvent.category == category

        )

        .order_by(
            PreferenceEvent.id.asc()
        )

        .all()

    )

    if events:

        return events

    history = (

        db.query(MemoryHistory)

        .filter(

            MemoryHistory.user_id == user_id,

            MemoryHistory.category == category

        )

        .order_by(
            MemoryHistory.id.asc()
        )

        .all()

    )

    return history


def detect_conflict(
    db,
    user_id,
    fact,
    category
):

    existing_memories = (
        db.query(Memory)
        .filter(
            Memory.user_id == user_id,
            Memory.category == category,
            Memory.active == True
        )
        .all()
    )

    if not existing_memories:
        return None

    incoming = fact.strip().lower()

    for memory in existing_memories:

        existing = memory.fact.strip().lower()

        # ---------------------------------
        # Exact Match
        # ---------------------------------

        if existing == incoming:

            return {
                "memory": memory,
                "conflict_score": 0.0,
                "poison_score": 0.0,
                "attack_type": "DUPLICATE"
            }

        # ---------------------------------
        # Preference Updates (Phase 3)
        # ---------------------------------

        if category in PREFERENCE_CATEGORIES:
            if not _is_exclusive_preference(fact, category):
                continue

            preference_history = (
                _get_preference_history(
                    db,
                    user_id,
                    category
                )
            )

            pref_result = detect_preference_update(
                old_fact=memory.fact,
                new_fact=fact,
                preference_history=preference_history
            )

            if pref_result["is_manipulation"]:

                return {
                    "memory": memory,
                    "conflict_score": 0.85,
                    "poison_score": pref_result[
                        "drift_score"
                    ],
                    "attack_type": "PREFERENCE_MANIPULATION",
                    "drift_score": pref_result[
                        "drift_score"
                    ],
                    "stability_score": pref_result[
                        "stability_score"
                    ],
                    "preference_result": pref_result,
                }

            return {
                "memory": memory,
                "conflict_score": 0.60,
                "poison_score": 0.0,
                "attack_type": "PREFERENCE_UPDATE",
                "drift_score": pref_result[
                    "drift_score"
                ],
                "stability_score": pref_result[
                    "stability_score"
                ],
                "preference_result": pref_result,
            }

        # ---------------------------------
        # Tool Policy Poisoning (Phase 4)
        # ---------------------------------

        if category in TOOL_POLICY_CATEGORIES:

            policy_result = (
                ToolPolicyValidator.compare_tool_policies(
                    old_policy=memory.fact,
                    new_policy=fact
                )
            )

            if policy_result["is_poison"]:

                return {
                    "memory": memory,
                    "conflict_score": 0.95,
                    "poison_score": policy_result[
                        "poison_score"
                    ],
                    "attack_type": "TOOL_POLICY_POISONING",
                    "violation_reason": policy_result.get(
                        "violation_reason"
                    ),
                }

            return {
                "memory": memory,
                "conflict_score": 0.60,
                "poison_score": 0.0,
                "attack_type": "TOOL_POLICY_UPDATE",
            }

        # ---------------------------------
        # False Fact Detection
        # ---------------------------------

        poison_result = detect_false_fact_injection(
            old_fact=memory.fact,
            new_fact=fact
        )

        if poison_result["is_poison"]:

            return {
                "memory": memory,
                "conflict_score": 0.95,
                "poison_score": poison_result[
                    "poison_score"
                ],
                "attack_type": "FALSE_FACT_INJECTION",
                "contradiction_score": poison_result[
                    "contradiction_score"
                ]
            }

        # ---------------------------------
        # Normal Conflict
        # ---------------------------------

        return {
            "memory": memory,
            "conflict_score": 0.60,
            "poison_score": 0.0,
            "attack_type": "NONE"
        }

    return None
