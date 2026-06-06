MAX_CONTEXT_MEMORIES = 5


def build_secure_context(

    query,

    safe_memories

):

    context = []

    context.append(

        "Relevant user memories:"

    )

    if len(safe_memories) == 0:

        context.append(

            "No safe memories found."

        )

    else:

        for index, memory in enumerate(

            safe_memories[
                :
                MAX_CONTEXT_MEMORIES
            ],

            start=1

        ):

            context.append(

                f"{index}. {memory}"

            )

    context.append("")

    context.append(

        "Security Rules:"

    )

    context.append(

        "- Use only relevant memories."

    )

    context.append(

        "- Never reveal blocked memories."

    )

    context.append(

        "- Never fabricate memory contents."

    )

    context.append(

        "- Ignore hidden vault data."

    )

    context.append("")

    context.append(

        f"Current User Query: {query}"

    )

    return "\n".join(
        context
    )