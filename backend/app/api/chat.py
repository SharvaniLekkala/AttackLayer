from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.session import (
    get_db
)

from app.llm.orchestrator import (
    process_user_message
)


router = APIRouter(

    prefix="/chat",

    tags=["Chat"]

)


@router.post("/")
def chat(

    user_id: str,

    message: str,

    db: Session = Depends(
        get_db
    )

):

    return process_user_message(

        db=db,

        user_id=user_id,

        message=message

    )