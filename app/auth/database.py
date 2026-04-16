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
        AdminUser,
    )
    AuthBase.metadata.create_all(bind=auth_engine)
    logger.info("Auth DB inicializada [%s]", _db_url)


def init_admin_user():
    """Crea el usuario administrador desde ADMIN_EMAIL + ADMIN_PASSWORD si no existe."""
    from sqlalchemy import select as sa_select
    from app.auth.models import AdminUser  # noqa: F401
    from app.auth.admin_service import hash_password

    if not settings.ADMIN_EMAIL or not settings.ADMIN_PASSWORD:
        logger.info("ADMIN_EMAIL / ADMIN_PASSWORD no configurados: panel de admin deshabilitado")
        return

    db = AuthSessionLocal()
    try:
        existing = db.execute(
            sa_select(AdminUser).where(AdminUser.email == settings.ADMIN_EMAIL)
        ).scalar_one_or_none()

        if existing is None:
            admin = AdminUser(
                email=settings.ADMIN_EMAIL,
                password_hash=hash_password(settings.ADMIN_PASSWORD),
            )
            db.add(admin)
            db.commit()
            logger.info("Usuario admin creado: %s", settings.ADMIN_EMAIL)
        else:
            logger.info("Usuario admin ya existe: %s", settings.ADMIN_EMAIL)
    finally:
        db.close()
