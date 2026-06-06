from sqlalchemy.orm import Session

from app.database.models import Memory

from app.memory.embedding_service import (
    generate_embedding
)

from app.memory.vector_storage import (
    semantic_search
)

from app.security.retrieval_gaurd import (
    filter_memories
)


def retrieve_memories(

    db: Session,

    user_id: str,

    query: str,

    top_k: int = 5

):

    # ==========================
    # Generate Query Embedding
    # ==========================

    query_embedding = generate_embedding(
        query
    )

    # ==========================
    # Semantic Search
    # ==========================

    vector_results = semantic_search(

        embedding=query_embedding,

        top_k=top_k

    )

    memory_ids = []

    if (

        vector_results

        and

        "ids" in vector_results

        and

        len(
            vector_results["ids"]
        ) > 0

    ):

        for memory_id in (

            vector_results["ids"][0]

        ):

            try:

                memory_ids.append(
                    int(memory_id)
                )

            except:

                pass

    # ==========================
    # Load Semantic Matches
    # ==========================

    memories = (

        db.query(Memory)

        .filter(

            Memory.id.in_(
                memory_ids
            ),

            Memory.user_id
            ==
            user_id

        )

        .all()

    )

    # ==========================
    # Fallback Personal Memory
    # ==========================

    if len(memories) < 3:

        additional = (

            db.query(Memory)

            .filter(

                Memory.user_id
                ==
                user_id,

                Memory.active
                ==
                True

            )

            .order_by(

                Memory.id.desc()

            )

            .limit(top_k)

            .all()

        )

        existing = {

            memory.id

            for memory

            in memories

        }

        for memory in additional:

            if (

                memory.id

                not in

                existing

            ):

                memories.append(
                    memory
                )

    # ==========================
    # Retrieval Security
    # ==========================

    security_result = (

        filter_memories(

            memories,

            query

        )

    )

    # ==========================
    # Response
    # ==========================

    return {

        "query":

            query,

        "semantic_matches":

            len(
                memories
            ),

        "safe_memories":

            [

                memory.fact

                for memory

                in

                security_result[
                    "allowed_memories"
                ]

            ],

        "blocked_count":

            len(

                security_result[
                    "blocked_memories"
                ]

            ),

        "blocked_reasons":

            security_result[
                "blocked_reasons"
            ]

    }