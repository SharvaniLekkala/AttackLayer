from app.security.semantic_engine import (
    get_embedding,
    cosine_similarity,
)


def calculate_preference_stability(
    preference_history
):

    if not preference_history:

        return 1.0

    version_count = len(
        preference_history
    )

    if version_count <= 1:

        return 1.0

    # More versions in a short lineage → lower stability
    stability = max(
        0.0,
        1.0 - ((version_count - 1) * 0.15)
    )

    return round(stability, 4)


def calculate_preference_drift(
    old_fact,
    new_fact
):

    old_embedding = get_embedding(
        old_fact
    )

    new_embedding = get_embedding(
        new_fact
    )

    similarity = cosine_similarity(
        old_embedding,
        new_embedding
    )

    drift = round(
        1.0 - similarity,
        4
    )

    return drift


def generate_drift_score(
    drift,
    stability
):

    # Legitimate preference changes have moderate drift
    # Suspicious manipulation: high drift + low stability
    drift_component = min(
        drift * 1.2,
        1.0
    )

    instability_component = 1.0 - stability

    score = (
        (drift_component * 0.55)
        +
        (instability_component * 0.45)
    )

    return round(
        min(score, 1.0),
        4
    )


def detect_preference_update(
    old_fact,
    new_fact,
    preference_history=None
):

    drift = calculate_preference_drift(
        old_fact,
        new_fact
    )

    stability = calculate_preference_stability(
        preference_history or []
    )

    drift_score = generate_drift_score(
        drift,
        stability
    )

    # Preference updates (Python → Java) are NOT poisoning
    is_legitimate_update = (
        drift_score < 0.75
    )

    is_manipulation = (
        drift_score >= 0.75
        and stability < 0.40
    )

    return {

        "drift": drift,

        "stability_score": stability,

        "drift_score": drift_score,

        "is_legitimate_update":
            is_legitimate_update,

        "is_manipulation":
            is_manipulation,

        "attack_type":
            "PREFERENCE_MANIPULATION"
            if is_manipulation
            else "PREFERENCE_UPDATE",

    }
