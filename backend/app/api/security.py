from fastapi import APIRouter

from app.security.security_gateway import evaluate_security
from app.security.security_classifier import classify_security
from app.security.intent_classifier import classify_intent

router = APIRouter(
    prefix="/security",
    tags=["Security Gateway"]
)


@router.post("/evaluate")
def evaluate(text: str):
    return evaluate_security(text)


@router.post("/classify")
def classify(text: str):
    return classify_security(text)


@router.post("/intent")
def classify_intent_endpoint(text: str):
    return classify_intent(text)