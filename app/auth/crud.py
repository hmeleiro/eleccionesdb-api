"""
Operaciones CRUD para la base de datos de autenticación.
"""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.auth.models import ApiKey, AuditLog, DeveloperAccount, EmailVerificationToken


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ─── Desarrolladores ────────────────────────────────────

def create_developer(
    db: Session,
    *,
    email: str,
    name: str,
    organization: str | None = None,
    intended_use: str | None = None,
) -> DeveloperAccount:
    dev = DeveloperAccount(
        email=email,
        name=name,
        organization=organization,
        intended_use=intended_use,
    )
    db.add(dev)
    db.commit()
    db.refresh(dev)
    return dev


def get_developer_by_email(db: Session, email: str) -> DeveloperAccount | None:
    return db.query(DeveloperAccount).filter(DeveloperAccount.email == email).first()


def get_developer_by_id(db: Session, developer_id: int) -> DeveloperAccount | None:
    return db.query(DeveloperAccount).filter(DeveloperAccount.id == developer_id).first()


def activate_developer(db: Session, developer: DeveloperAccount) -> None:
    developer.email_verified = True
    developer.status = "active"
    developer.updated_at = _utcnow()
    db.commit()


# ─── Tokens de verificación ─────────────────────────────

def create_verification_token(
    db: Session,
    *,
    developer_id: int,
    token_hash: str,
    expires_at: datetime,
) -> EmailVerificationToken:
    token = EmailVerificationToken(
        developer_id=developer_id,
        token_hash=token_hash,
        expires_at=expires_at,
    )
    db.add(token)
    db.commit()
    db.refresh(token)
    return token


def get_valid_verification_token(
    db: Session, token_hash: str
) -> EmailVerificationToken | None:
    """Busca un token válido: no usado y no expirado."""
    now = _utcnow()
    return (
        db.query(EmailVerificationToken)
        .filter(
            EmailVerificationToken.token_hash == token_hash,
            EmailVerificationToken.used_at.is_(None),
            EmailVerificationToken.expires_at > now,
        )
        .first()
    )


def mark_token_used(db: Session, token: EmailVerificationToken) -> None:
    token.used_at = _utcnow()
    db.commit()


def get_latest_token_created_at(
    db: Session, developer_id: int
) -> datetime | None:
    """Devuelve la fecha de creación del último token de un desarrollador."""
    token = (
        db.query(EmailVerificationToken)
        .filter(EmailVerificationToken.developer_id == developer_id)
        .order_by(EmailVerificationToken.created_at.desc())
        .first()
    )
    return token.created_at if token else None


# ─── API Keys ────────────────────────────────────────────

def create_api_key(
    db: Session,
    *,
    developer_id: int,
    key_prefix: str,
    key_hash: str,
    label: str | None = None,
) -> ApiKey:
    api_key = ApiKey(
        developer_id=developer_id,
        key_prefix=key_prefix,
        key_hash=key_hash,
        label=label,
    )
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    return api_key


def get_active_api_key_by_hash(db: Session, key_hash: str) -> ApiKey | None:
    """Busca una API key activa por su hash.

    Incluye claves cuya revoked_at esté en el futuro (periodo de gracia en rotación).
    """
    now = _utcnow()
    return (
        db.query(ApiKey)
        .filter(
            ApiKey.key_hash == key_hash,
            ApiKey.is_active == True,  # noqa: E712
            (ApiKey.revoked_at.is_(None)) | (ApiKey.revoked_at > now),
            (ApiKey.expires_at.is_(None)) | (ApiKey.expires_at > now),
        )
        .first()
    )


def get_active_keys_for_developer(db: Session, developer_id: int) -> list[ApiKey]:
    """Devuelve todas las claves activas (sin revocar) de un desarrollador."""
    now = _utcnow()
    return (
        db.query(ApiKey)
        .filter(
            ApiKey.developer_id == developer_id,
            ApiKey.is_active == True,  # noqa: E712
            (ApiKey.revoked_at.is_(None)) | (ApiKey.revoked_at > now),
        )
        .all()
    )


def revoke_api_key(db: Session, api_key: ApiKey, *, immediate: bool = True) -> None:
    """Revoca una API key. Si immediate=False, se usa el revoked_at ya configurado (periodo de gracia)."""
    if immediate:
        api_key.revoked_at = _utcnow()
    api_key.is_active = False
    db.commit()


def schedule_revoke_api_key(db: Session, api_key: ApiKey, revoke_at: datetime) -> None:
    """Programa la revocación futura de una API key (periodo de gracia)."""
    api_key.revoked_at = revoke_at
    db.commit()


def update_last_used(db: Session, api_key: ApiKey) -> None:
    api_key.last_used_at = _utcnow()
    db.commit()


# ─── Auditoría ───────────────────────────────────────────

def create_audit_entry(
    db: Session,
    *,
    developer_id: int | None,
    event_type: str,
    ip_address: str | None = None,
    details: str | None = None,
) -> AuditLog:
    entry = AuditLog(
        developer_id=developer_id,
        event_type=event_type,
        ip_address=ip_address,
        details=details,
    )
    db.add(entry)
    db.commit()
    return entry
