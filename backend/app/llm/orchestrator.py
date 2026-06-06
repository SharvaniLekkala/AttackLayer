from sqlalchemy.orm import Session

from app.memory.retrieval import (
    retrieve_memories
)

from app.security.context_builder import (
    build_secure_context
)

from app.llm.service import (
    generate_response
)

from app.security.security_gateway import (
    evaluate_security
)

from app.memory.vault import (
    create_memory
)

from app.security.response_guard import (
    filter_response
)

from app.audit.logger import (
    log_security_event
)

from app.memory.memory_normalizer import (
    normalize_memory
)
from app.security.memory_worthiness import (
    should_store_memory
)
def process_user_message(

    db: Session,

    user_id: str,

    message: str

):

    # =====================================
    # Security Evaluation
    # =====================================

    security_result = (

        evaluate_security(
            message
        )

    )

    operation = (

        security_result[
            "operation"
        ]

    )

    # =====================================
    # Log EVERY Prompt
    # =====================================

    log_security_event(

        db=db,

        operation=operation,

        decision=

            security_result[
                "decision"
            ],

        threat=

            security_result[
                "threat"
            ],

        risk_score=

            security_result[
                "risk_score"
            ],

        payload=message

    )

    # =====================================
    # Block
    # =====================================

    if (

        security_result[
            "decision"
        ]

        ==

        "BLOCK"

    ):

        return {

            "response":

                "I can't retain sensitive "
                "credentials or secret "
                "information.",

            "retrieved_memories":

                [],

            "security":

                security_result,

            "memory":

                None

        }

    # =====================================
    # General Chat
    # =====================================

    if (

        operation

        ==

        "GENERAL_CHAT"

    ):

        llm_response = (

            generate_response(

                query=message,

                secure_context=""

            )

        )

        guard_result = (

            filter_response(

                llm_response

            )

        )

        return {

            "response":

                guard_result[
                    "response"
                ],

            "retrieved_memories":

                [],

            "security":

                security_result,

            "memory":

                None

        }

    # =====================================
    # Memory Read
    # =====================================

    if (

        operation

        ==

        "READ"

    ):

        retrieval_result = (

            retrieve_memories(

                db=db,

                user_id=user_id,

                query=message

            )

        )

        secure_context = (

            build_secure_context(

                query=message,

                safe_memories=

                    retrieval_result[
                        "safe_memories"
                    ]

            )

        )

        llm_response = (

            generate_response(

                query=message,

                secure_context=

                    secure_context

            )

        )

        guard_result = (

            filter_response(

                llm_response

            )

        )

        return {

            "response":

                guard_result[
                    "response"
                ],

            "retrieved_memories":

                retrieval_result[
                    "safe_memories"
                ],

            "security":

                security_result,

            "memory":

                None

        }

    # =====================================
    # Memory Write
    # =====================================

    if (

        operation

        ==

        "WRITE"

    ):

        normalized_fact = (

            normalize_memory(

                message

            )

        )
        worth = should_store_memory(

            normalized_fact

        )

        if not worth["store"]:

            return {

                "response":

                    "Understood.",

                "retrieved_memories":

                    [],

                "security":

                        security_result,

                "memory":

                    None

            }
        memory_result = (

            create_memory(

                db=db,

                user_id=user_id,

                fact=normalized_fact

            )

        )

        return {

            "response":

                "Got it. "
                "I'll remember that.",

            "retrieved_memories":

                [],

            "security":

                security_result,

            "memory":

                memory_result

        }

    # =====================================
    # Memory Update
    # =====================================

    if (

        operation

        ==

        "UPDATE"

    ):

        normalized_fact = (

    normalize_memory(

                message

            )

        )

        memory_result = (

            create_memory(

                db=db,

                user_id=user_id,

                fact=normalized_fact

            )

)
        return {

            "response":

                "Got it. "
                "I've updated that information.",

            "retrieved_memories":

                [],

            "security":

                security_result,

            "memory":

                memory_result

        }

    # =====================================
    # Fallback
    # =====================================

    llm_response = (

        generate_response(

            query=message,

            secure_context=""

        )

    )

    guard_result = (

        filter_response(

            llm_response

        )

    )

    return {

        "response":

            guard_result[
                "response"
            ],

        "retrieved_memories":

            [],

        "security":

            security_result,

        "memory":

            None

    }
