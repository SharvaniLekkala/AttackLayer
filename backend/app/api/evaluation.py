from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.evaluation.metrics import compute_classification_metrics
from app.learning.classification_tracker import get_learning_stats
from app.research.poisoning_dataset import POISONING_DATASET

router = APIRouter(prefix="/evaluation", tags=["Evaluation"])


@router.get("/metrics")
def get_metrics(db: Session = Depends(get_db)):
    return compute_classification_metrics(db)


@router.get("/learning")
def get_learning(db: Session = Depends(get_db)):
    return get_learning_stats(db)


@router.get("/poisoning-dataset")
def get_poisoning_dataset():
    return {
        "categories": list(POISONING_DATASET.keys()),
        "total_examples": sum(len(v) for v in POISONING_DATASET.values()),
        "dataset": POISONING_DATASET,
    }
@router.get("/research-metrics")
def get_research_metrics(
    db: Session = Depends(get_db)
):
    return compute_classification_metrics(db)