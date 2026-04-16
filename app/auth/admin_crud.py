"""Operaciones CRUD para el panel de administración."""

import math
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import func, select, delete
from sqlalchemy.orm import Session

from app.auth.models import AdminUser, AuditLog, ApiKey, DeveloperAccount


# ── Usuarios admin ────────────────────────────────────────

def get_admin_by_email(db: Session, email: str) -> Optional[AdminUser]:
    return db.execute(
        select(AdminUser).where(AdminUser.email == email)
    ).scalar_one_or_none()


# ── Desarrolladores ───────────────────────────────────────

def list_developers(
    db: Session,
    *,
    status: Optional[str] = None,
    email_search: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    page: int = 1,
    per_page: int = 25,
) -> tuple[list[DeveloperAccount], int]:
    """Devuelve (items, total) con filtros y paginación."""
    q = select(DeveloperAccount)
    if status:
        q = q.where(DeveloperAccount.status == status)
    if email_search:
        q = q.where(DeveloperAccount.email.ilike(f"%{email_search}%"))
    if date_from:
        q = q.where(DeveloperAccount.created_at >= date_from)
    if date_to:
        q = q.where(DeveloperAccount.created_at <= date_to)

    count_q = select(func.count()).select_from(q.subquery())
    total = db.execute(count_q).scalar_one()

    offset = (page - 1) * per_page
    items = db.execute(
        q.order_by(DeveloperAccount.created_at.desc()).offset(offset).limit(per_page)
    ).scalars().all()

    return list(items), total


def get_developer_detail(db: Session, developer_id: int) -> Optional[DeveloperAccount]:
    """Devuelve el desarrollador con sus claves; audit_log se carga aparte."""
    return db.execute(
        select(DeveloperAccount).where(DeveloperAccount.id == developer_id)
    ).scalar_one_or_none()


def get_developer_audit_log(db: Session, developer_id: int, limit: int = 50) -> list[AuditLog]:
    return db.execute(
        select(AuditLog)
        .where(AuditLog.developer_id == developer_id)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
    ).scalars().all()


def update_developer_status(db: Session, developer_id: int, new_status: str) -> Optional[DeveloperAccount]:
    dev = db.execute(
        select(DeveloperAccount).where(DeveloperAccount.id == developer_id)
    ).scalar_one_or_none()
    if dev is None:
        return None
    dev.status = new_status
    dev.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(dev)
    return dev


def revoke_all_keys(db: Session, developer_id: int) -> int:
    """Revoca todas las claves activas del desarrollador. Devuelve el nº revocadas."""
    now = datetime.now(timezone.utc)
    keys = db.execute(
        select(ApiKey).where(
            ApiKey.developer_id == developer_id,
            ApiKey.is_active == True,  # noqa: E712
        )
    ).scalars().all()
    for key in keys:
        key.is_active = False
        key.revoked_at = now
    db.commit()
    return len(keys)


def delete_developer(db: Session, developer_id: int) -> bool:
    """Elimina en cascada el desarrollador y todos sus registros relacionados."""
    dev = db.execute(
        select(DeveloperAccount).where(DeveloperAccount.id == developer_id)
    ).scalar_one_or_none()
    if dev is None:
        return False

    # Borrar registros relacionados explícitamente (sin CASCADE en SQLite)
    db.execute(delete(AuditLog).where(AuditLog.developer_id == developer_id))
    db.execute(delete(ApiKey).where(ApiKey.developer_id == developer_id))

    from app.auth.models import EmailVerificationToken
    db.execute(
        delete(EmailVerificationToken).where(
            EmailVerificationToken.developer_id == developer_id
        )
    )

    db.delete(dev)
    db.commit()
    return True
