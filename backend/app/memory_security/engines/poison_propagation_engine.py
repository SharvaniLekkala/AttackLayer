from app.database.models import (
    Memory,
    PropagationEvent,
)

from app.memory.vault import (
    create_memory,
    get_memory_by_id,
)

from app.security.security_gateway import (
    evaluate_security
)

from app.memory_security.services.propagation_event_logger import (
    log_propagation_event
)

from app.memory_security.services.poison_event_logger import (
    log_poison_event
)

from app.memory_security.constants import (
    PROPAGATION_ATTACK,
)


POISON_PROPAGATION_THRESHOLD = 0.65


class PoisonPropagationEngine:

    @staticmethod
    def get_root_memory_id(
        db,
        memory_id
    ):

        memory = get_memory_by_id(
            db,
            memory_id
        )

        if not memory:

            return memory_id

        current = memory

        while current.parent_memory_id:

            parent = get_memory_by_id(
                db,
                current.parent_memory_id
            )

            if not parent:

                break

            current = parent

        return current.id

    @staticmethod
    def _collect_propagated_agents(
        db,
        root_memory_id
    ):

        agents = set()

        root = get_memory_by_id(
            db,
            root_memory_id
        )

        if not root:

            return agents

        agents.add(root.user_id)

        frontier = [root_memory_id]

        visited = {root_memory_id}

        while frontier:

            children = (

                db.query(Memory)

                .filter(
                    Memory.parent_memory_id.in_(
                        frontier
                    )
                )

                .all()

            )

            frontier = []

            for child in children:

                if child.id in visited:

                    continue

                visited.add(child.id)

                agents.add(child.user_id)

                frontier.append(child.id)

        return agents

    @staticmethod
    def calculate_spread_rate(
        db,
        memory_id,
        total_agents=5
    ):

        root_id = (
            PoisonPropagationEngine.get_root_memory_id(
                db,
                memory_id
            )
        )

        agents = (
            PoisonPropagationEngine._collect_propagated_agents(
                db,
                root_id
            )
        )

        if total_agents <= 0:

            total_agents = 1

        spread_rate = round(
            len(agents) / total_agents,
            4
        )

        spread_percentage = round(
            spread_rate * 100,
            2
        )

        return {

            "root_memory_id": root_id,

            "infected_agents": sorted(
                list(agents)
            ),

            "infected_count":
                len(agents),

            "total_agents":
                total_agents,

            "spread_rate":
                spread_rate,

            "spread_percentage":
                spread_percentage,

        }

    @staticmethod
    def trace_propagation_chain(
        db,
        memory_id
    ):

        root_id = (
            PoisonPropagationEngine.get_root_memory_id(
                db,
                memory_id
            )
        )

        events = (

            db.query(PropagationEvent)

            .filter(
                PropagationEvent.root_memory_id
                ==
                root_id
            )

            .order_by(
                PropagationEvent.id.asc()
            )

            .all()

        )

        root_memory = get_memory_by_id(
            db,
            root_id
        )

        origin_agent = (
            root_memory.user_id
            if root_memory
            else "unknown"
        )

        chain = [origin_agent]

        hops = []

        for event in events:

            hops.append({

                "from":
                    event.origin_agent,

                "to":
                    event.target_agent,

                "decision":
                    event.decision,

                "spread_percentage":
                    event.spread_percentage,

                "poison_score":
                    event.poison_score,

                "attack_type":
                    event.attack_type,

                "time":
                    event.created_at.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),

            })

            if (
                event.target_agent
                not in chain
            ):

                chain.append(
                    event.target_agent
                )

        return {

            "root_memory_id": root_id,

            "origin_agent": origin_agent,

            "chain": chain,

            "path":
                " -> ".join(chain),

            "hops": hops,

            "hop_count": len(hops),

        }

    @staticmethod
    def _build_propagation_path(
        db,
        memory_id,
        target_agent
    ):

        trace = (
            PoisonPropagationEngine.trace_propagation_chain(
                db,
                memory_id
            )
        )

        chain = trace["chain"]

        if target_agent not in chain:

            chain = chain + [target_agent]

        return " -> ".join(chain)

    @staticmethod
    def _should_block_propagation(
        source_memory,
        security_result
    ):

        if security_result["decision"] == "BLOCK":

            return True

        if source_memory.poison_flag:

            return True

        if (
            source_memory.poison_score
            >=
            POISON_PROPAGATION_THRESHOLD
        ):

            return True

        return False

    @staticmethod
    def propagate_memory(
        db,
        memory_id,
        origin_agent,
        target_agent,
        total_agents=5
    ):

        source_memory = get_memory_by_id(
            db,
            memory_id
        )

        if not source_memory:

            return {

                "status": "error",

                "message":
                    "Memory not found",

            }

        if not source_memory.active:

            return {

                "status": "error",

                "message":
                    "Cannot propagate inactive memory",

            }

        root_id = (
            PoisonPropagationEngine.get_root_memory_id(
                db,
                memory_id
            )
        )

        security_result = evaluate_security(
            source_memory.fact
        )

        poison_score = max(
            source_memory.poison_score,
            security_result.get(
                "risk_score",
                0.0
            )
        )

        attack_type = (
            source_memory.attack_type
            if source_memory.attack_type
            != "NONE"
            else (
                PROPAGATION_ATTACK
                if poison_score
                >= POISON_PROPAGATION_THRESHOLD
                else "NONE"
            )
        )

        spread_data = (
            PoisonPropagationEngine.calculate_spread_rate(
                db,
                memory_id,
                total_agents=total_agents
            )
        )

        propagation_path = (
            PoisonPropagationEngine._build_propagation_path(
                db,
                memory_id,
                target_agent
            )
        )

        blocked = (
            PoisonPropagationEngine._should_block_propagation(
                source_memory,
                security_result
            )
        )

        if blocked:

            event = log_propagation_event(

                db=db,

                memory_id=memory_id,

                origin_agent=origin_agent,

                target_agent=target_agent,

                propagation_path=
                    propagation_path,

                spread_score=
                    spread_data[
                        "spread_rate"
                    ],

                fact=source_memory.fact,

                poison_score=poison_score,

                attack_type=
                    PROPAGATION_ATTACK,

                spread_percentage=
                    spread_data[
                        "spread_percentage"
                    ],

                decision="BLOCK",

                root_memory_id=root_id,

            )

            log_poison_event(

                db=db,

                attack_type=
                    PROPAGATION_ATTACK,

                poison_score=poison_score,

                decision="BLOCK",

                details=(
                    f"Propagation blocked: "
                    f"{origin_agent} -> "
                    f"{target_agent}: "
                    f"{source_memory.fact}"
                ),

                memory_id=memory_id,

            )

            return {

                "status": "blocked",

                "attack_type":
                    PROPAGATION_ATTACK,

                "decision": "BLOCK",

                "propagation_event_id":
                    event.id,

                "spread_rate":
                    spread_data[
                        "spread_rate"
                    ],

                "spread_percentage":
                    spread_data[
                        "spread_percentage"
                    ],

                "propagation_path":
                    propagation_path,

                "message":
                    "Poisoned memory propagation blocked",

            }

        memory_result = create_memory(
            db=db,
            user_id=target_agent,
            fact=source_memory.fact
        )

        if memory_result.get(
            "status"
        ) in (
            "blocked",
            "quarantined"
        ):

            event = log_propagation_event(

                db=db,

                memory_id=memory_id,

                origin_agent=origin_agent,

                target_agent=target_agent,

                propagation_path=
                    propagation_path,

                spread_score=
                    spread_data[
                        "spread_rate"
                    ],

                fact=source_memory.fact,

                poison_score=poison_score,

                attack_type=(
                    memory_result.get(
                        "attack_type",
                        PROPAGATION_ATTACK
                    )
                ),

                spread_percentage=
                    spread_data[
                        "spread_percentage"
                    ],

                decision=(
                    memory_result.get(
                        "status",
                        "BLOCK"
                    ).upper()
                ),

                root_memory_id=root_id,

            )

            return {

                "status":
                    memory_result.get(
                        "status"
                    ),

                "attack_type":
                    memory_result.get(
                        "attack_type"
                    ),

                "propagation_event_id":
                    event.id,

                "spread_rate":
                    spread_data[
                        "spread_rate"
                    ],

                "spread_percentage":
                    spread_data[
                        "spread_percentage"
                    ],

                "propagation_path":
                    propagation_path,

                "memory": memory_result,

            }

        new_memory_id = memory_result.get(
            "memory_id"
        )

        if new_memory_id:

            propagated = get_memory_by_id(
                db,
                new_memory_id
            )

            if propagated:

                propagated.parent_memory_id = (
                    memory_id
                )

                propagated.source = (
                    f"PROPAGATED_FROM_"
                    f"{origin_agent}"
                )

                db.commit()

        updated_spread = (
            PoisonPropagationEngine.calculate_spread_rate(
                db,
                new_memory_id
                or memory_id,
                total_agents=total_agents
            )
        )

        event = log_propagation_event(

            db=db,

            memory_id=(
                new_memory_id
                or memory_id
            ),

            origin_agent=origin_agent,

            target_agent=target_agent,

            propagation_path=
                propagation_path,

            spread_score=
                updated_spread[
                    "spread_rate"
                ],

            fact=source_memory.fact,

            poison_score=poison_score,

            attack_type=attack_type,

            spread_percentage=
                updated_spread[
                    "spread_percentage"
                ],

            decision="ALLOW",

            root_memory_id=root_id,

        )

        if (
            poison_score
            >=
            POISON_PROPAGATION_THRESHOLD
        ):

            log_poison_event(

                db=db,

                attack_type=
                    PROPAGATION_ATTACK,

                poison_score=poison_score,

                decision="ALLOW_WITH_WARNING",

                details=(
                    f"High-risk memory propagated: "
                    f"{origin_agent} -> "
                    f"{target_agent}"
                ),

                memory_id=(
                    new_memory_id
                    or memory_id
                ),

            )

        return {

            "status": "propagated",

            "decision": "ALLOW",

            "propagation_event_id":
                event.id,

            "new_memory_id":
                new_memory_id,

            "spread_rate":
                updated_spread[
                    "spread_rate"
                ],

            "spread_percentage":
                updated_spread[
                    "spread_percentage"
                ],

            "infected_agents":
                updated_spread[
                    "infected_agents"
                ],

            "propagation_path":
                propagation_path,

            "chain": (
                PoisonPropagationEngine.trace_propagation_chain(
                    db,
                    new_memory_id
                    or memory_id
                )
            ),

            "memory": memory_result,

        }
