from app.security.semantic_engine import (
    get_embedding,
    cosine_similarity,
)

from app.database.models import Memory


OPERATION_EXAMPLES = {

    "WRITE": [

        "Remember that I am a security analyst",
        "Store this information",
        "Save this memory",
        "Remember my preference",
        "Add this to memory",
        "Keep this in memory",
        "Memorize this fact",

        "Remember that I use Python to code",
        "Remember that I work as an engineer",
        "Save that I prefer Linux",
        "Store that I live in Hyderabad",

        "I live in Hyderabad",
        "I work as an AI engineer",
        "I am a security analyst",
        "My favorite language is Python",
        "My favorite food is pizza",
        "I study AI and Data Science",
        "I like Java",
        "I prefer Linux",
        "My hometown is Chennai",

        "Professor Smith approved Project X",
        "The meeting is on Friday",
        "The project deadline is June 30",
        "The server is located in Mumbai",
        "John is the manager",

        "Store that Professor Smith approved Project X",
        "Remember that my favorite language is Python",
        "Save that I prefer Java",

    ],

    "READ": [

        "What do you remember about me",
        "Show my memories",
        "Tell me my stored information",
        "Retrieve my memory",
        "What is stored in memory",
        "Show all memories",
        "Who am I",
        "Where do I live",
        "What do I work as",
        "Tell me everything you know about me",

        "What is my favorite language",
        "Which language do I prefer",
        "What language do I like",
        "Tell me my favorite language",
        "Do you remember my favorite language",
        "What do you know about my preferences",
        "What food do I like",
        "What is my hometown",
        "Do you remember where I live",
        "What do you know about me",
        "Recall my preferences",
        "Recall my stored facts",

    ],

    "UPDATE": [

        "Update my memory",
        "Change my location",
        "Replace my old information",
        "Modify the stored memory",
        "Remember instead that I live in Delhi",
        "Overwrite previous memory",

        "I moved to Bangalore",
        "I now live in Chennai",
        "My favorite language is Java now",
        "I prefer Java instead of Python",
        "I changed my favorite language",
        "Update my favorite language",
        "I no longer like Python",
        "Replace Python with Java",
        "Actually I use Java to code now",

    ],

    "GENERAL_CHAT": [

        "Hello",
        "How are you",
        "Tell me a joke",
        "Explain machine learning",
        "What is Python",
        "Who won the match",
        "What is artificial intelligence",
        "Write a poem",
        "How does deep learning work",
        "What is the weather today",

    ],
}

QUESTION_EXAMPLES = OPERATION_EXAMPLES["READ"]

MEMORY_COMMAND_EXAMPLES = [

    "Remember that I am a security analyst",
    "Store this information",
    "Save this memory",
    "Remember my preference",
    "Add this to memory",
    "Keep this in memory",
    "Memorize this fact",
    "Remember that I use Python to code",
    "Remember that I work as an engineer",
    "Save that I prefer Linux",
    "Store that I live in Hyderabad",
    "Store that Professor Smith approved Project X",
    "Remember that my favorite language is Python",
    "Save that I prefer Java",

]

DECLARATIVE_EXAMPLES = [

    "I live in Hyderabad",
    "I work as an AI engineer",
    "I am a security analyst",
    "My favorite language is Python",
    "My favorite food is pizza",
    "I study AI and Data Science",
    "I like Java",
    "I prefer Linux",
    "My hometown is Chennai",
    "Professor Smith approved Project X",
    "The meeting is on Friday",

]

CLOSE_SCORE_DELTA = 0.06
MEMORY_RELEVANCE_THRESHOLD = 0.52


def _build_embedding_cache(examples):

    return [

        get_embedding(example)

        for example in examples

    ]


OPERATION_EMBEDDINGS = {

    operation: _build_embedding_cache(examples)

    for operation, examples

    in OPERATION_EXAMPLES.items()

}

QUESTION_EMBEDDINGS = _build_embedding_cache(
    QUESTION_EXAMPLES
)

MEMORY_COMMAND_EMBEDDINGS = _build_embedding_cache(
    MEMORY_COMMAND_EXAMPLES
)

DECLARATIVE_EMBEDDINGS = _build_embedding_cache(
    DECLARATIVE_EXAMPLES
)


def _max_similarity(
    embedding,
    prototype_embeddings
):

    if not prototype_embeddings:

        return 0.0

    return max(

        cosine_similarity(
            embedding,
            prototype
        )

        for prototype

        in prototype_embeddings

    )


def _compute_operation_scores(embedding):

    scores = {}

    for operation, prototypes in (

        OPERATION_EMBEDDINGS.items()

    ):

        scores[operation] = round(

            _max_similarity(
                embedding,
                prototypes
            ),

            4

        )

    return scores


def _compute_intent_scores(embedding):

    return {

        "question": round(

            _max_similarity(
                embedding,
                QUESTION_EMBEDDINGS
            ),

            4

        ),

        "memory_command": round(

            _max_similarity(
                embedding,
                MEMORY_COMMAND_EMBEDDINGS
            ),

            4

        ),

        "declarative": round(

            _max_similarity(
                embedding,
                DECLARATIVE_EMBEDDINGS
            ),

            4

        ),

    }


def _has_relevant_memory(
    db,
    user_id,
    embedding
):

    memories = (

        db.query(Memory)

        .filter(

            Memory.user_id == user_id,

            Memory.active == True

        )

        .all()

    )

    if not memories:

        return False

    for memory in memories:

        memory_embedding = get_embedding(
            memory.fact
        )

        similarity = cosine_similarity(
            embedding,
            memory_embedding
        )

        if (

            similarity
            >=
            MEMORY_RELEVANCE_THRESHOLD

        ):

            return True

    return False


def _resolve_write_vs_update(
    write_score,
    update_score,
    db,
    user_id,
    embedding
):

    has_memory = (

        db is not None

        and

        user_id is not None

        and

        _has_relevant_memory(
            db,
            user_id,
            embedding
        )

    )

    if (

        abs(
            write_score - update_score
        )

        <=
        CLOSE_SCORE_DELTA

    ):

        return (
            "UPDATE"
            if has_memory
            else "WRITE"
        )

    if update_score > write_score:

        return (
            "UPDATE"
            if has_memory
            else "WRITE"
        )

    return "WRITE"


def _apply_intent_layer(
    scores,
    intent_scores
):

    question = intent_scores["question"]

    memory_command = intent_scores["memory_command"]

    declarative = intent_scores["declarative"]

    best_operation = max(
        scores,
        key=scores.get
    )

    best_score = scores[best_operation]

    memory_peak = max(
        scores["WRITE"],
        scores["READ"],
        scores["UPDATE"]
    )

    # Clear general chat wins over memory operations
    if (

        scores["GENERAL_CHAT"]
        >
        memory_peak + 0.12

    ):

        return (
            "GENERAL_CHAT",
            scores["GENERAL_CHAT"]
        )

    # Question intent → READ
    if (

        question
        >
        memory_command + 0.02

        and

        question
        >
        declarative + 0.02

    ):

        if (

            scores["READ"]
            >=
            scores["WRITE"] - 0.10

        ):

            best_operation = "READ"

            best_score = scores["READ"]

    # Memory command or declarative fact → WRITE
    elif (

        memory_command
        >
        question + 0.02

        or

        (
            declarative
            >
            question + 0.02

            and

            scores["WRITE"]
            >=
            scores["READ"] - 0.08
        )

    ):

        if (

            scores["WRITE"]
            >=
            scores["GENERAL_CHAT"] - 0.05

        ):

            best_operation = "WRITE"

            best_score = scores["WRITE"]

    # GENERAL_CHAT only when clearly non-memory
    elif (

        best_operation == "GENERAL_CHAT"

    ):

        memory_peak = max(

            scores["WRITE"],

            scores["READ"],

            scores["UPDATE"]

        )

        if (

            memory_peak
            >
            scores["GENERAL_CHAT"] - 0.06

        ):

            ranked_memory = sorted(

                [
                    ("WRITE", scores["WRITE"]),
                    ("READ", scores["READ"]),
                    ("UPDATE", scores["UPDATE"]),
                ],

                key=lambda item: item[1],

                reverse=True

            )

            best_operation = ranked_memory[0][0]

            best_score = ranked_memory[0][1]

    return best_operation, best_score


def analyze_request(
    text: str,
    db=None,
    user_id=None
):

    embedding = get_embedding(text)

    scores = _compute_operation_scores(
        embedding
    )

    intent_scores = _compute_intent_scores(
        embedding
    )

    operation, confidence = _apply_intent_layer(
        scores,
        intent_scores
    )

    # WRITE vs UPDATE disambiguation
    if operation in ("WRITE", "UPDATE"):

        operation = _resolve_write_vs_update(

            scores["WRITE"],

            scores["UPDATE"],

            db,

            user_id,

            embedding

        )

        confidence = scores[operation]

    ranked = sorted(

        scores.items(),

        key=lambda item: item[1],

        reverse=True

    )

    alternatives = [

        item

        for item in ranked

        if item[0] != operation

    ][:3]

    return {

        "operation": operation,

        "confidence": confidence,

        "scores": scores,

        "intent_scores": intent_scores,

        "alternatives": alternatives,

    }
