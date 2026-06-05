from app.security.semantic_engine import (
    get_embedding,
    cosine_similarity,
    mean_embedding
)


OPERATION_EXAMPLES = {

    "WRITE": [

        "Remember that I am a security analyst",
        "Store this information",
        "Save this memory",
        "Remember my preference",
        "Add this to memory",
        "Remember that I live in Hyderabad"
    ],

    "READ": [

        "What do you remember about me",
        "Show my memories",
        "Tell me my stored information",
        "Retrieve my memory",
        "What is stored in memory",
        "Show all memories"
    ],

    "UPDATE": [

        "Update my memory",
        "Change my location",
        "Replace my old information",
        "Modify the stored memory",
        "Remember instead that I live in Delhi",
        "Overwrite previous memory"
    ],

    "GENERAL_CHAT": [

        "Hello",
        "How are you",
        "Tell me a joke",
        "Explain machine learning",
        "What is Python",
        "Who won the match"
    ]
}


OPERATION_CENTROIDS = {}

for operation, examples in OPERATION_EXAMPLES.items():

    embeddings = [
        get_embedding(example)
        for example in examples
    ]

    OPERATION_CENTROIDS[operation] = (
        mean_embedding(embeddings)
    )


def analyze_request(text: str):

    embedding = get_embedding(text)

    scores = []

    for operation, centroid in (
        OPERATION_CENTROIDS.items()
    ):

        similarity = cosine_similarity(
            embedding,
            centroid
        )

        scores.append(
            (
                operation,
                round(similarity, 4)
            )
        )

    scores.sort(
        key=lambda x: x[1],
        reverse=True
    )

    best_operation = scores[0][0]
    confidence = scores[0][1]

    return {
        "operation": best_operation,
        "confidence": confidence,
        "alternatives": scores[1:4]
    }