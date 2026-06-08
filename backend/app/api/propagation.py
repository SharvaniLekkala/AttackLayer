from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.session import (
    get_db
)

from app.memory_security.engines.poison_propagation_engine import (
    PoisonPropagationEngine
)

router = APIRouter(
    prefix="/propagation",
    tags=["Propagation"]
)


@router.post("/propagate")
def propagate_memory(
    memory_id: int,
    origin_agent: str,
    target_agent: str,
    total_agents: int = 5,
    db: Session = Depends(get_db)
):

    return PoisonPropagationEngine.propagate_memory(
        db=db,
        memory_id=memory_id,
        origin_agent=origin_agent,
        target_agent=target_agent,
        total_agents=total_agents
    )


@router.get("/spread-rate/{memory_id}")
def spread_rate(
    memory_id: int,
    total_agents: int = 5,
    db: Session = Depends(get_db)
):

    return PoisonPropagationEngine.calculate_spread_rate(
        db=db,
        memory_id=memory_id,
        total_agents=total_agents
    )


@router.get("/chain/{memory_id}")
def propagation_chain(
    memory_id: int,
    db: Session = Depends(get_db)
):

    return PoisonPropagationEngine.trace_propagation_chain(
        db=db,
        memory_id=memory_id
    )
