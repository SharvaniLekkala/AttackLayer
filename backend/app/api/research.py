from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.session import get_db

from app.audit.research_metrics import (
    get_scenario_metrics,
    get_poison_attempts_over_time,
    get_attack_distribution,
    get_trust_distribution_chart,
    get_spread_rate_chart,
    get_conflict_frequency,
    get_quarantine_memories,
    get_poison_events,
)

from app.research.attack_scenario_runner import (
    run_false_fact_scenario,
    run_preference_scenario,
    run_tool_usage_scenario,
    run_propagation_scenario,
    run_all_scenarios,
)

from app.memory_security.tool_policy_config import (
    APPROVED_DOMAINS,
    APPROVED_APIS,
    TRUSTED_TOOLS,
)

router = APIRouter(
    prefix="/research",
    tags=["Research"],
)


@router.get("/scenarios")
def scenario_metrics(
    db: Session = Depends(get_db),
):
    return get_scenario_metrics(db)


@router.post("/run-all")
def run_all(
    db: Session = Depends(get_db),
):
    return run_all_scenarios(db)


@router.post("/run/false-fact")
def run_false_fact(
    db: Session = Depends(get_db),
):
    return run_false_fact_scenario(db)


@router.post("/run/preference")
def run_preference(
    db: Session = Depends(get_db),
):
    return run_preference_scenario(db)


@router.post("/run/tool-usage")
def run_tool_usage(
    db: Session = Depends(get_db),
):
    return run_tool_usage_scenario(db)


@router.post("/run/propagation")
def run_propagation(
    db: Session = Depends(get_db),
):
    return run_propagation_scenario(db)


@router.get("/charts/poison-timeline")
def poison_timeline_chart(
    db: Session = Depends(get_db),
):
    return get_poison_attempts_over_time(db)


@router.get("/charts/attack-distribution")
def attack_distribution_chart(
    db: Session = Depends(get_db),
):
    return get_attack_distribution(db)


@router.get("/charts/trust-distribution")
def trust_distribution_chart(
    db: Session = Depends(get_db),
):
    return get_trust_distribution_chart(db)


@router.get("/charts/spread-rate")
def spread_rate_chart(
    db: Session = Depends(get_db),
):
    return get_spread_rate_chart(db)


@router.get("/charts/conflict-frequency")
def conflict_frequency(
    db: Session = Depends(get_db),
):
    return {
        "conflict_count": get_conflict_frequency(db)
    }


@router.get("/quarantine")
def quarantine_list(
    db: Session = Depends(get_db),
):
    return get_quarantine_memories(db)


@router.get("/poison-events")
def poison_events_list(
    db: Session = Depends(get_db),
):
    return get_poison_events(db)


@router.get("/trusted-tools")
def trusted_tools_config():
    return {
        "approved_domains": sorted(APPROVED_DOMAINS),
        "approved_apis": sorted(APPROVED_APIS),
        "trusted_tools": sorted(TRUSTED_TOOLS),
    }
