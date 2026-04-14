"""
Base de datos SQLite independiente para el sistema de autenticación.

Completamente separada de la base de datos PostgreSQL de datos electorales.
"""

import logging
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

logger = logging.getLogger("uvicorn.error")

# ── Engine SQLite ────────────────────────────────────────

_db_url = settings.AUTH_DB_URL

# Crear directorio padre si no existe (ej: /app/data/)
if _db_url.startswith("sqlite:///") and _db_url != "sqlite:///:memory:":
    db_path = _db_url.replace("sqlite:///", "", 1)
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

auth_engine = create_engine(
    _db_url,
    connect_args={"check_same_thread": False},  # necesario para SQLite + FastAPI
    pool_pre_ping=True,
)


# Activar WAL mode y foreign keys en cada conexión SQLite
@event.listens_for(auth_engine, "connect")
def _set_sqlite_pragmas(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


AuthSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=auth_engine)

AuthBase = declarative_base()


# ── Dependency de FastAPI ────────────────────────────────

def get_auth_db():
    """Proporciona una sesión de la BD de auth y la cierra al terminar."""
    db = AuthSessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Inicialización de tablas ─────────────────────────────

def init_auth_db():
    """Crea todas las tablas del sistema de auth si no existen.

    Seguro para llamar en cada arranque (checkfirst=True por defecto).
    """
    from app.auth.models import (  # noqa: F401 – import para registrar los modelos en AuthBase
        DeveloperAccount,
        ApiKey,
        EmailVerificationToken,
        AuditLog,
    )
    AuthBase.metadata.create_all(bind=auth_engine)
    logger.info("Auth DB inicializada [%s]", _db_url)
