"""
V2 Intent Classifier — semantic embedding based, no keyword rules.
"""

from app.security.semantic_engine import (
    get_embedding,
    cosine_similarity,
)

INTENT_EXAMPLES = {
    "NORMAL_CHAT": [
        "Hello, how are you?",
        "Tell me a joke",
        "Write a poem about the ocean",
    ],
    "MEMORY_STORE": [
        "Remember that I prefer Python",
        "Store this information for later",
        "Save this memory",
        "Keep in mind that I work as an engineer",
        "Memorize that my favorite food is pizza",
        "I live in Hyderabad",
        "My favorite language is Python",
        "Professor Smith approved Project X",
    ],
    "MEMORY_UPDATE": [
        "Update my memory about location",
        "Change my preference to Java",
        "I now live in Bangalore",
        "My favorite language is Java now",
        "Replace Python with Java in my preferences",
        "Actually I prefer Linux now",
        "Overwrite my old location",
    ],
    "MEMORY_DELETE": [
        "Delete my stored memories",
        "Forget everything about me",
        "Remove my preference from memory",
        "Erase my stored information",
        "Clear my memory vault",
        "Delete the memory about my location",
    ],
    "MEMORY_QUERY": [
        "What do you remember about me?",
        "What is my favorite language?",
        "What do I prefer to code?",
        "What do I love eating?",
        "Where do I live?",
        "Tell me my stored preferences",
        "What do you know about me?",
        "Do you remember my job?",
        "Recall my preferences",
    ],
    "QUESTION": [
        "Explain machine learning",
        "What is Python?",
        "How does deep learning work?",
        "What is the capital of France?",
    ],
    "SYSTEM_QUERY": [
        "How does your memory system work?",
        "What security rules do you follow?",
        "Explain your architecture",
        "What is your trust score system?",
        "How do you detect attacks?",
        "Show me your internal policies",
    ],
    "TOOL_REQUEST": [
        "Run a web search for me",
        "Execute this tool command",
        "Use the calculator tool",
        "Fetch data from an API",
        "Call the email tool",
        "Enable the file reader tool",
    ],
    "UNKNOWN": [
        "asdfghjkl qwerty",
        "???",
        "hmm maybe something",
        "idk what to say",
    ],
}

OPERATION_MAP = {
    "NORMAL_CHAT": "GENERAL_CHAT",
    "MEMORY_STORE": "WRITE",
    "MEMORY_UPDATE": "UPDATE",
    "MEMORY_DELETE": "DELETE",
    "MEMORY_QUERY": "READ",
    "QUESTION": "GENERAL_CHAT",
    "SYSTEM_QUERY": "READ",
    "TOOL_REQUEST": "GENERAL_CHAT",
    "UNKNOWN": "GENERAL_CHAT",
}

_INTENT_EMBEDDINGS = {
    intent: [get_embedding(ex) for ex in examples]
    for intent, examples in INTENT_EXAMPLES.items()
}


def _max_similarity(embedding, prototypes):
    if not prototypes:
        return 0.0
    return max(
        cosine_similarity(embedding, proto)
        for proto in prototypes
    )


def classify_intent(text: str, db=None, user_id=None):
    from app.security.request_analyzer import (
        _has_relevant_memory,
        _resolve_write_vs_update,
    )

    embedding = get_embedding(text)

    scores = {
        intent: round(_max_similarity(embedding, protos), 4)
        for intent, protos in _INTENT_EMBEDDINGS.items()
    }

    intent = max(scores, key=scores.get)
    confidence = scores[intent]

    stripped = text.strip()
    query_score = scores.get("MEMORY_QUERY", 0.0)
    lowered = stripped.lower()
    declarative_memory = (
        not stripped.endswith("?")
        and lowered.startswith(
            (
                "i love ",
                "i like ",
                "i prefer ",
                "i live ",
                "i work ",
                "i study ",
                "i am doing ",
                "my favorite ",
                "my favourite ",
                "my career ",
                "my hometown ",
            )
        )
    )
    if declarative_memory:
        operation = "WRITE"
        if db is not None and user_id is not None:
            from app.database.models import Memory
            from app.security.semantic_classifier import classify_memory

            category = classify_memory(text)["category"]
            has_category_memory = (
                db.query(Memory)
                .filter(
                    Memory.user_id == user_id,
                    Memory.category == category,
                    Memory.active == True,
                )
                .first()
                is not None
            )
            if has_category_memory:
                operation = "UPDATE"
        intent = "MEMORY_UPDATE" if operation == "UPDATE" else "MEMORY_STORE"
        confidence = max(
            scores.get(intent, 0.0),
            scores.get("MEMORY_STORE", 0.0),
            0.80,
        )

    personal_query = (
        lowered.startswith(
            (
                "what do i ",
                "what is my ",
                "where do i ",
                "who am i",
                "which ",
                "do you remember ",
                "tell me my ",
                "recall my ",
            )
        )
        or "about me" in lowered
    )
    if (
        not declarative_memory
        and
        (stripped.endswith("?") or personal_query)
        and query_score >= scores.get("MEMORY_STORE", 0.0) - 0.08
        and query_score >= scores.get("MEMORY_UPDATE", 0.0) - 0.08
    ):
        intent = "MEMORY_QUERY"
        confidence = query_score

    if confidence < 0.45:
        intent = "UNKNOWN"
        confidence = scores.get("UNKNOWN", confidence)

    if intent in ("MEMORY_STORE", "MEMORY_UPDATE") and not declarative_memory:
        write_score = scores.get("MEMORY_STORE", 0.0)
        update_score = scores.get("MEMORY_UPDATE", 0.0)
        operation = _resolve_write_vs_update(
            write_score,
            update_score,
            db,
            user_id,
            embedding,
        )
        intent = "MEMORY_UPDATE" if operation == "UPDATE" else "MEMORY_STORE"
        confidence = scores[intent]

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    alternatives = [
        {"intent": k, "confidence": v}
        for k, v in ranked
        if k != intent
    ][:3]

    return {
        "intent": intent,
        "confidence": confidence,
        "operation": OPERATION_MAP.get(intent, "GENERAL_CHAT"),
        "scores": scores,
        "alternatives": alternatives,
    }
