from fastapi import APIRouter

from app.security.semantic_classifier import (
    classify_memory
)

router = APIRouter(
    prefix="/classifier",
    tags=["Semantic Classifier"]
)


@router.post("/classify")
def classify(text: str):

    return classify_memory(text)