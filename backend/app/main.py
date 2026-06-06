from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.session import engine
from app.database.session import Base
import app.database.models
from app.api.memory import router as memory_router
from app.api.classifier import (
    router as classifier_router
)
from app.api.threat import (
    router as threat_router
)
from app.api.sensitive import (
    router as sensitive_router
)
from app.api.request_analyzer import (
    router as request_router
)
from app.api.security import (
    router as security_router
)
from app.api.audit import (
    router as audit_router
)
from app.api.chat import (
    router as chat_router
)
from app.api.export import (
    router as export_router
)
app = FastAPI(
    title="AttackLayer",
    description="Semantic Security Firewall for Long-Term Memory in LLM Agents",
    version="1.0.0"
)
Base.metadata.create_all(bind=engine)
app.include_router(memory_router)
app.include_router(classifier_router)
app.include_router(
    threat_router
)

app.include_router(
    sensitive_router
)
app.include_router(
    request_router
)
app.include_router(
    security_router
)
app.include_router(
    audit_router
)
app.include_router(
    chat_router
)
app.include_router(

    export_router

)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "project": "AttackLayer",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }