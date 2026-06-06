from fastapi import APIRouter
from fastapi.responses import FileResponse

from sqlalchemy import create_engine
import pandas as pd

router = APIRouter(

    prefix="/export",

    tags=["Export"]

)

DATABASE = "sqlite:///attacklayer.db"


@router.get(
    "/audit-csv"
)
def export_audit():

    engine = create_engine(

        DATABASE

    )

    df = pd.read_sql(

        "SELECT * FROM audit_events",

        engine

    )

    filename = "audit.csv"

    df.to_csv(

        filename,

        index=False

    )

    return FileResponse(

        filename,

        media_type="text/csv",

        filename=filename

    )


@router.get(
    "/memory-csv"
)
def export_memory():

    engine = create_engine(

        DATABASE

    )

    df = pd.read_sql(

        "SELECT * FROM memories",

        engine

    )

    filename = "memory_vault.csv"

    df.to_csv(

        filename,

        index=False

    )

    return FileResponse(

        filename,

        media_type="text/csv",

        filename=filename

    )


@router.get(
    "/history-csv"
)
def export_history():

    engine = create_engine(

        DATABASE

    )

    df = pd.read_sql(

        "SELECT * FROM memory_history",

        engine

    )

    filename = "memory_history.csv"

    df.to_csv(

        filename,

        index=False

    )

    return FileResponse(

        filename,

        media_type="text/csv",

        filename=filename

    )