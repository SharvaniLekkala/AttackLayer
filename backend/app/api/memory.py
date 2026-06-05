from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.session import get_db

from app.memory.vault import (
    create_memory,
    get_all_memories,
    get_memory_by_id,
    archive_memory
)

router = APIRouter(
    prefix="/memory",
    tags=["Memory Vault"]
)


@router.post("/create")
def create_memory_api(

    user_id: str,
    fact: str,

    db: Session = Depends(get_db)

):
    return create_memory(
        db,
        user_id,
        fact
    )


@router.get("/all")
def get_memories(

    db: Session = Depends(get_db)

):
    return get_all_memories(db)


@router.get("/{memory_id}")
def get_memory(

    memory_id: int,

    db: Session = Depends(get_db)

):
    return get_memory_by_id(
        db,
        memory_id
    )


@router.delete("/{memory_id}")
def archive_memory_api(

    memory_id: int,

    db: Session = Depends(get_db)

):
    return archive_memory(
        db,
        memory_id
    )