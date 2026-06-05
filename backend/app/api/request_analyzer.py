from fastapi import APIRouter

from app.security.request_analyzer import (
    analyze_request
)

router = APIRouter(
    prefix="/request",
    tags=["Request Analyzer"]
)


@router.post("/analyze")
def analyze(text: str):

    return analyze_request(text)