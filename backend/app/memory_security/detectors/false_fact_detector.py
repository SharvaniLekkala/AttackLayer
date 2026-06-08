import re


NEGATIVE_WORDS = {

    "not",
    "never",
    "no",
    "none",

    "reject",
    "rejected",

    "deny",
    "denied",

    "false",

    "incorrect",

    "failed",

    "cancelled",

    "canceled"

}


POSITIVE_WORDS = {

    "approved",
    "accept",
    "accepted",

    "true",

    "correct",

    "passed",

    "confirmed",

    "verified"

}


def normalize_text(text):

    return (
        text
        .lower()
        .strip()
    )


def calculate_fact_similarity(
    old_fact,
    new_fact
):

    old_words = set(
        re.findall(
            r"\w+",
            normalize_text(old_fact)
        )
    )

    new_words = set(
        re.findall(
            r"\w+",
            normalize_text(new_fact)
        )
    )

    if not old_words:

        return 0.0

    overlap = len(
        old_words.intersection(
            new_words
        )
    )

    union = len(
        old_words.union(
            new_words
        )
    )

    return round(
        overlap / union,
        4
    )


def calculate_contradiction_score(
    old_fact,
    new_fact
):

    old_lower = normalize_text(
        old_fact
    )

    new_lower = normalize_text(
        new_fact
    )

    old_positive = any(
        word in old_lower
        for word in POSITIVE_WORDS
    )

    new_negative = any(
        word in new_lower
        for word in NEGATIVE_WORDS
    )

    old_negative = any(
        word in old_lower
        for word in NEGATIVE_WORDS
    )

    new_positive = any(
        word in new_lower
        for word in POSITIVE_WORDS
    )

    if (
        old_positive
        and
        new_negative
    ):

        return 0.95

    if (
        old_negative
        and
        new_positive
    ):

        return 0.95

    return 0.0


def generate_poison_score(
    similarity,
    contradiction_score
):

    if contradiction_score > 0.8:

        return 0.90

    if similarity > 0.8:

        return 0.20

    return 0.0


def detect_false_fact_injection(
    old_fact,
    new_fact
):

    similarity = (

        calculate_fact_similarity(
            old_fact,
            new_fact
        )

    )

    contradiction_score = (

        calculate_contradiction_score(
            old_fact,
            new_fact
        )

    )

    poison_score = (

        generate_poison_score(
            similarity,
            contradiction_score
        )

    )

    return {

        "similarity":
            similarity,

        "contradiction_score":
            contradiction_score,

        "poison_score":
            poison_score,

        "is_poison":

            poison_score >= 0.80

    }