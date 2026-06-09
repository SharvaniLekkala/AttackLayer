"""
Lightweight SQLite migration — adds V2 columns to existing tables.
"""

from sqlalchemy import inspect, text
from app.database.session import engine

MEMORY_COLUMNS = {
    "importance_score": "FLOAT DEFAULT 0.5",
    "verification_count": "INTEGER DEFAULT 0",
    "conflict_count": "INTEGER DEFAULT 0",
    "usage_count": "INTEGER DEFAULT 0",
    "attack_history": "VARCHAR DEFAULT ''",
    "status": "VARCHAR DEFAULT 'ACTIVE'",
}

AUDIT_COLUMNS = {
    "intent": "VARCHAR DEFAULT 'UNKNOWN'",
    "intent_confidence": "FLOAT DEFAULT 0.0",
    "attack_type": "VARCHAR DEFAULT 'SAFE'",
    "attack_confidence": "FLOAT DEFAULT 0.0",
    "risk_level": "VARCHAR DEFAULT 'LOW'",
    "memory_category": "VARCHAR DEFAULT 'GENERAL'",
    "conflict_status": "VARCHAR DEFAULT 'NONE'",
    "trust_scores": "VARCHAR DEFAULT '[]'",
    "retrieved_memories": "VARCHAR DEFAULT ''",
    "memories_used": "VARCHAR DEFAULT ''",
    "poison_detected": "BOOLEAN DEFAULT 0",
    "quarantine_status": "VARCHAR DEFAULT 'NONE'",
    "response_confidence": "FLOAT DEFAULT 0.0",
    "memory_confidence": "FLOAT DEFAULT 0.0",
    "security_confidence": "FLOAT DEFAULT 0.0",
    "execution_time_ms": "FLOAT DEFAULT 0.0",
    "final_decision": "VARCHAR DEFAULT 'ALLOW'",
    "explanation": "VARCHAR DEFAULT ''",
}


def _add_missing_columns(table_name, column_defs):
    inspector = inspect(engine)
    if table_name not in inspector.get_table_names():
        return

    existing = {col["name"] for col in inspector.get_columns(table_name)}

    with engine.begin() as conn:
        for col_name, col_type in column_defs.items():
            if col_name not in existing:
                conn.execute(
                    text(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}")
                )


def run_migrations():
    _add_missing_columns("memories", MEMORY_COLUMNS)
    _add_missing_columns("audit_events", AUDIT_COLUMNS)
