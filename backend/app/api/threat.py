from fastapi import APIRouter

from app.security.threat_detector import (
    detect_threat
)

router = APIRouter(
    prefix="/threat",
    tags=["Threat Detector"]
)


@router.post("/detect")
def detect(text: str):

    return detect_threat(text)