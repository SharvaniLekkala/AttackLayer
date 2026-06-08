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


def _build_memory_response(
    memory_result,
    stored_message="Got it. I'll remember that."
):

    if not memory_result:

        return stored_message

    status = memory_result.get("status")

    if status == "blocked":

        return (
            "⚠ Memory update blocked.\n\n"
            "Reason: "
            + memory_result.get(
                "attack_type",
                "Security Policy"
            )
            + "\n\nOriginal memory preserved."
        )

    if status == "quarantined":

        return (
            "⚠ Memory sent for "
            "security review."
        )

    if status == "duplicate":

        return "I already know that."

    return stored_message


def _handle_memory_store(
    db,
    user_id,
    message,
    security_result,
    stored_message="Got it. I'll remember that."
):

    normalized_fact = normalize_memory(
        message
    )

    worth = should_store_memory(
        normalized_fact
    )

    if not worth["store"]:

        return {

            "response": "Understood.",

            "retrieved_memories": [],

            "security": security_result,

            "memory": None

        }

    memory_result = create_memory(
        db=db,
        user_id=user_id,
        fact=normalized_fact
    )

    return {

        "response": _build_memory_response(
            memory_result,
            stored_message=stored_message
        ),

        "retrieved_memories": [],

        "security": security_result,

        "memory": memory_result

    }


def process_user_message(

    db: Session,

    user_id: str,

    message: str

):

    # =====================================
    # Security Evaluation
    # =====================================

    security_result = evaluate_security(
        message,
        db=db,
        user_id=user_id
    )

    operation = security_result["operation"]

    # =====================================
    # Log Every Prompt
    # =====================================

    log_security_event(

        db=db,

        operation=operation,

        decision=security_result["decision"],

        threat=security_result["threat"],

        risk_score=security_result["risk_score"],

        payload=message

    )

    # =====================================
    # Immediate Block
    # =====================================

    if security_result["decision"] == "BLOCK":

        block_response = (
            "I can't retain sensitive "
            "credentials or secret "
            "information."
        )

        if security_result.get(
            "tool_policy_type"
        ):

            block_response = (
                "⚠ Unsafe tool policy blocked.\n\n"
                "Reason: TOOL_POLICY_POISONING"
            )

            violation = security_result.get(
                "tool_policy_violation"
            )

            if violation:

                block_response += (
                    "\n"
                    + violation
                )

        return {

            "response": block_response,

            "retrieved_memories": [],

            "security": security_result,

            "memory": None

        }

    # =====================================
    # General Chat
    # =====================================

    if operation == "GENERAL_CHAT":

        llm_response = generate_response(
            query=message,
            secure_context=""
        )

        guard_result = filter_response(
            llm_response
        )

        return {

            "response": guard_result["response"],

            "retrieved_memories": [],

            "security": security_result,

            "memory": None

        }

    # =====================================
    # Memory Read
    # =====================================

    if operation == "READ":

        retrieval_result = retrieve_memories(
            db=db,
            user_id=user_id,
            query=message
        )

        secure_context = build_secure_context(
            query=message,
            safe_memories=retrieval_result[
                "safe_memories"
            ]
        )

        llm_response = generate_response(
            query=message,
            secure_context=secure_context
        )

        guard_result = filter_response(
            llm_response
        )

        return {

            "response": guard_result["response"],

            "retrieved_memories": retrieval_result[
                "safe_memories"
            ],

            "security": security_result,

            "memory": None

        }

    # =====================================
    # Memory Write
    # =====================================

    if operation == "WRITE":

        return _handle_memory_store(
            db=db,
            user_id=user_id,
            message=message,
            security_result=security_result
        )

    # =====================================
    # Memory Update
    # =====================================

    if operation == "UPDATE":

        return _handle_memory_store(
            db=db,
            user_id=user_id,
            message=message,
            security_result=security_result,
            stored_message=(
                "Got it. I've updated "
                "your memory."
            )
        )

    # =====================================
    # Fallback
    # =====================================

    llm_response = generate_response(
        query=message,
        secure_context=""
    )

    guard_result = filter_response(
        llm_response
    )

    return {

        "response": guard_result["response"],

        "retrieved_memories": [],

        "security": security_result,

        "memory": None

    }
