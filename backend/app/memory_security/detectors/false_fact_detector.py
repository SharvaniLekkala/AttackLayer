import re
from app.memory.embedding_service import generate_embedding
from app.security.semantic_engine import cosine_similarity
import numpy as np


def extract_entities(text):
    """Extract potential entities (proper nouns, numbers, dates) from text."""
    # Simple entity extraction - in production, use NER
    entities = []

    # Extract numbers
    numbers = re.findall(r'\b\d+(?:\.\d+)?\b', text)
    entities.extend([('NUMBER', num) for num in numbers])

    # Extract potential proper nouns (capitalized words)
    words = text.split()
    for i, word in enumerate(words):
        if word[0].isupper() and len(word) > 1:
            # Check if it's not at the start of sentence (simplistic)
            if i > 0 and words[i-1][-1] not in '.!?':
                entities.append(('PROPER_NOUN', word))
            elif i == 0:  # First word of sentence
                entities.append(('PROPER_NOUN', word))

    # Extract dates (simple patterns)
    date_patterns = [
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
        r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',
        r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b'
    ]
    for pattern in date_patterns:
        dates = re.findall(pattern, text, re.IGNORECASE)
        entities.extend([('DATE', date) for date in dates])

    return entities


def calculate_semantic_similarity(old_fact, new_fact):
    """Calculate semantic similarity using embeddings."""
    try:
        old_embedding = generate_embedding(old_fact)
        new_embedding = generate_embedding(new_fact)
        return cosine_similarity(old_embedding, new_embedding)
    except Exception:
        # Fallback to word overlap if embedding fails
        return calculate_word_overlap_similarity(old_fact, new_fact)


def calculate_word_overlap_similarity(old_fact, new_fact):
    """Calculate similarity based on word overlap."""
    old_words = set(re.findall(r'\w+', old_fact.lower()))
    new_words = set(re.findall(r'\w+', new_fact.lower()))

    if not old_words:
        return 0.0

    overlap = len(old_words.intersection(new_words))
    union = len(old_words.union(new_words))

    return round(overlap / union, 4) if union > 0 else 0.0


def detect_numerical_contradiction(old_fact, new_fact):
    """Detect if numerical values have been changed contradictorily."""
    old_numbers = re.findall(r'\b\d+(?:\.\d+)?\b', old_fact)
    new_numbers = re.findall(r'\b\d+(?:\.\d+)?\b', new_fact)

    if not old_numbers and not new_numbers:
        return 0.0, False

    if not old_numbers or not new_numbers:
        # One has numbers, the other doesn't - potential contradiction
        return 0.5, True

    # Compare numerical values
    contradictions = 0
    total_comparisons = 0

    # Simple comparison: if same count of numbers, compare pairwise
    if len(old_numbers) == len(new_numbers):
        for old_num, new_num in zip(old_numbers, new_numbers):
            total_comparisons += 1
            if old_num != new_num:
                contradictions += 1
    else:
        # Different number of numbers - likely contradiction
        contradictions = 1
        total_comparisons = 1

    score = contradictions / max(total_comparisons, 1)
    return score, score > 0.5


def detect_entity_contradiction(old_fact, new_fact):
    """Detect if entities have been changed contradictorily."""
    old_entities = extract_entities(old_fact)
    new_entities = extract_entities(new_fact)

    if not old_entities and not new_entities:
        return 0.0, False

    # Convert to sets for comparison
    old_set = set(old_entities)
    new_set = set(new_entities)

    if not old_set:
        return 0.3 if new_set else 0.0, bool(new_set)

    if not new_set:
        return 0.3 if old_set else 0.0, bool(old_set)

    # Check for conflicting entities (same type but different value)
    old_by_type = {}
    new_by_type = {}

    for entity_type, entity_value in old_entities:
        if entity_type not in old_by_type:
            old_by_type[entity_type] = []
        old_by_type[entity_type].append(entity_value.lower())

    for entity_type, entity_value in new_entities:
        if entity_type not in new_by_type:
            new_by_type[entity_type] = []
        new_by_type[entity_type].append(entity_value.lower())

    contradictions = 0
    total_types = 0

    # Check each entity type
    all_types = set(old_by_type.keys()) | set(new_by_type.keys())
    for entity_type in all_types:
        total_types += 1
        old_values = set(old_by_type.get(entity_type, []))
        new_values = set(new_by_type.get(entity_type, []))

        # If both have values of this type but they're different, it's a contradiction
        if old_values and new_values and not (old_values & new_values):
            contradictions += 1

    score = contradictions / max(total_types, 1)
    return score, score > 0.3


def detect_linguistic_contradiction(old_fact, new_fact):
    """Detect contradictions based on linguistic patterns."""
    old_lower = old_fact.lower()
    new_lower = new_fact.lower()

    # Positive/Negative word pairs
    positive_words = {
        'approved', 'accepted', 'true', 'correct', 'passed', 'confirmed',
        'verified', 'affirmed', 'ratified', 'endorsed', 'valid', 'legitimate',
        'authentic', 'genuine', 'real', 'actual', 'factual', 'accurate'
    }

    negative_words = {
        'not', 'never', 'no', 'none', 'reject', 'rejected', 'deny', 'denied',
        'false', 'incorrect', 'failed', 'cancelled', 'canceled', 'invalid',
        'illegitimate', 'inauthentic', 'spurious', 'bogus', 'fabricated',
        'fictitious', 'untrue', 'unaccurate', 'mistaken', 'wrong'
    }

    # Check for positive in old and negative in new
    old_positive = any(word in old_lower for word in positive_words)
    new_negative = any(word in new_lower for word in negative_words)

    # Check for negative in old and positive in new
    old_negative = any(word in old_lower for word in negative_words)
    new_positive = any(word in new_lower for word in positive_words)

    if (old_positive and new_negative) or (old_negative and new_positive):
        return 0.9

    # Check for contradiction words
    contradiction_pairs = [
        ('increased', 'decreased'), ('rose', 'fell'), ('grew', 'shrank'),
        ('expanded', 'contracted'), ('added', 'removed'), ('inserted', 'deleted'),
        ('created', 'destroyed'), ('built', 'demolished'), ('made', 'broken'),
        ('fixed', 'broken'), ('working', 'broken'), ('open', 'closed'),
        ('on', 'off'), ('yes', 'no'), ('true', 'false'), ('correct', 'incorrect')
    ]

    for pos_word, neg_word in contradiction_pairs:
        if (pos_word in old_lower and neg_word in new_lower) or \
           (neg_word in old_lower and pos_word in new_lower):
            return 0.85

    return 0.0


def generate_poison_score(similarity, contradiction_score, linguistic_score=0.0, numerical_score=0.0, entity_score=0.0):
    """
    Generate poison score based on multiple factors.
    Returns a score between 0.0 and 1.0 where higher means more likely to be poison.
    """
    # Start with base score from contradiction
    base_score = contradiction_score

    # Boost score if we have high similarity AND contradiction (suggests deliberate fact replacement)
    if similarity > 0.8 and contradiction_score > 0.5:
        base_score = min(1.0, base_score + 0.2)

    # Boost score if we have strong linguistic contradiction
    if linguistic_score > 0.8:
        base_score = min(1.0, base_score + 0.15)

    # Boost score if we have numerical or entity contradictions
    if numerical_score > 0.7 or entity_score > 0.7:
        base_score = min(1.0, base_score + 0.1)

    # Reduce score if similarity is low (less likely to be deliberate fact replacement)
    if similarity < 0.5:
        base_score = base_score * 0.7

    # Ensure score is in valid range
    return max(0.0, min(1.0, base_score))


def detect_false_fact_injection(old_fact, new_fact):
    """
    Enhanced false fact injection detection.

    Returns:
    {
        "similarity": float,  # Semantic similarity (0-1)
        "contradiction_score": float,  # Contradiction likelihood (0-1)
        "poison_score": float,  # Overall poison score (0-1)
        "is_poison": bool,  # Whether this is detected as poison
        "confidence": str,  # Confidence level: "high", "medium", "low"
        "details": dict  # Additional details about the detection
    }
    """
    # Handle edge cases
    if not old_fact or not new_fact:
        return {
            "similarity": 0.0,
            "contradiction_score": 0.0,
            "poison_score": 0.0,
            "is_poison": False,
            "confidence": "low",
            "details": {"reason": "Empty fact(s)"}
        }

    # If facts are identical after normalization, it's not false fact injection
    if old_fact.strip().lower() == new_fact.strip().lower():
        return {
            "similarity": 1.0,
            "contradiction_score": 0.0,
            "poison_score": 0.0,
            "is_poison": False,
            "confidence": "high",
            "details": {"reason": "Identical facts"}
        }

    # Calculate different types of similarity and contradiction
    semantic_similarity = calculate_semantic_similarity(old_fact, new_fact)
    word_similarity = calculate_word_overlap_similarity(old_fact, new_fact)

    # Use the higher of the two similarities
    similarity = max(semantic_similarity, word_similarity)

    # Calculate contradiction scores from different methods
    ling_contradiction = detect_linguistic_contradiction(old_fact, new_fact)
    num_contradiction, num_contradiction_flag = detect_numerical_contradiction(old_fact, new_fact)
    ent_contradiction, ent_contradiction_flag = detect_entity_contradiction(old_fact, new_fact)

    # Combine contradiction scores (weighted average)
    contradiction_score = max(
        ling_contradiction,
        num_contradiction * 0.8,  # Numerical contradictions are strong but might be legitimate updates
        ent_contradiction * 0.7   # Entity changes might be legitimate in some contexts
    )

    # Generate poison score based on all factors
    poison_score = generate_poison_score(
        similarity=similarity,
        contradiction_score=contradiction_score,
        linguistic_score=ling_contradiction,
        numerical_score=num_contradiction,
        entity_score=ent_contradiction
    )

    # Determine confidence level based on poison_score and other factors
    if poison_score >= 0.8:
        confidence = "high"
    elif poison_score >= 0.5:
        confidence = "medium"
    else:
        confidence = "low"

    # Determine if it's poison based on confidence and other factors
    # We consider it poison if:
    # 1. High confidence (≥0.8 poison score) OR
    # 2. Medium confidence with strong evidence (specific contradiction types)
    is_poison = (
        poison_score >= 0.8 or  # High confidence
        (poison_score >= 0.6 and (num_contradiction_flag or ent_contradiction_flag)) or  # Medium confidence with specific evidence
        (ling_contradiction > 0.85)  # Very strong linguistic contradiction
    )

    # Prepare details
    details = {
        "semantic_similarity": round(semantic_similarity, 4),
        "word_similarity": round(word_similarity, 4),
        "linguistic_contradiction": round(ling_contradiction, 4),
        "numerical_contradiction": round(num_contradiction, 4),
        "entity_contradiction": round(ent_contradiction, 4),
        "combined_contradiction": round(contradiction_score, 4),
        "similarity_used": round(similarity, 4)
    }

    # Add flags if specific contradictions were detected
    if num_contradiction_flag:
        details["numerical_change_detected"] = True
    if ent_contradiction_flag:
        details["entity_change_detected"] = True

    return {
        "similarity": round(similarity, 4),
        "contradiction_score": round(contradiction_score, 4),
        "poison_score": round(poison_score, 4),
        "is_poison": is_poison,
        "confidence": confidence,
        "details": details
    }