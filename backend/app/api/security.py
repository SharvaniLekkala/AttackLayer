from fastapi import APIRouter

from app.security.security_gateway import (
    evaluate_security
)

router = APIRouter(
    prefix="/security",
    tags=["Security Gateway"]
)


@router.post("/evaluate")
def evaluate(text: str):

    return evaluate_security(text)