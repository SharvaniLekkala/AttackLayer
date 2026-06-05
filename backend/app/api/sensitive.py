from fastapi import APIRouter

from app.security.sensitive_detector import (
    detect_sensitive_data
)

router = APIRouter(
    prefix="/sensitive",
    tags=["Sensitive Detector"]
)


@router.post("/detect")
def detect(text: str):

    return detect_sensitive_data(text)