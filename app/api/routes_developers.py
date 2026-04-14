"""
Endpoints de gestión de cuenta de desarrollador y API keys.

Requieren autenticación via X-API-Key.
"""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.auth import crud
from app.auth.database import get_auth_db
from app.auth.dependencies import get_current_developer
from app.auth.models import DeveloperAccount
from app.auth.schemas import ApiKeyResponse, DeveloperProfileResponse, RevokeResponse
from app.auth.service import generate_api_key
from app.config import settings

router = APIRouter(prefix="/v1/developers", tags=["Desarrolladores"])


def _get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


# ─── Perfil ──────────────────────────────────────────────

@router.get("/me", response_model=DeveloperProfileResponse)
def get_profile(
    developer: DeveloperAccount = Depends(get_current_developer),
    db: Session = Depends(get_auth_db),
):
    """Devuelve el perfil del desarrollador autenticado."""
    active_keys = crud.get_active_keys_for_developer(db, developer.id)
    active_key = active_keys[0] if active_keys else None

    return DeveloperProfileResponse(
        id=developer.id,
        email=developer.email,
        name=developer.name,
        organization=developer.organization,
        status=developer.status,
        created_at=developer.created_at,
        api_key_prefix=active_key.key_prefix if active_key else None,
        api_key_created_at=active_key.created_at if active_key else None,
    )


# ─── Rotación de API key ────────────────────────────────

@router.post("/me/api-keys/rotate", response_model=ApiKeyResponse)
def rotate_api_key(
    request: Request,
    developer: DeveloperAccount = Depends(get_current_developer),
    db: Session = Depends(get_auth_db),
):
    """Rota la API key: revoca la actual (con periodo de gracia) y genera una nueva.

    La clave anterior seguirá funcionando durante el periodo de gracia configurado.
    La nueva clave se muestra una sola vez en la respuesta.
    """
    if developer.status != "active":
        raise HTTPException(status_code=403, detail="Cuenta no activa")

    # Revocar claves activas actuales con periodo de gracia
    active_keys = crud.get_active_keys_for_developer(db, developer.id)
    grace_until = datetime.now(timezone.utc) + timedelta(hours=settings.API_KEY_ROTATION_GRACE_HOURS)
    for key in active_keys:
        crud.schedule_revoke_api_key(db, key, revoke_at=grace_until)

    # Generar nueva clave
    full_key, prefix, key_hash = generate_api_key()
    crud.create_api_key(
        db,
        developer_id=developer.id,
        key_prefix=prefix,
        key_hash=key_hash,
        label="rotated",
    )

    client_ip = _get_client_ip(request)
    crud.create_audit_entry(
        db,
        developer_id=developer.id,
        event_type="key_rotated",
        ip_address=client_ip,
        details=f"new_prefix={prefix}",
    )

    return ApiKeyResponse(
        api_key=full_key,
        key_prefix=prefix,
        message="Nueva API key generada. La clave anterior seguirá funcionando durante "
        f"{settings.API_KEY_ROTATION_GRACE_HOURS}h. Guarda esta clave, no se mostrará de nuevo.",
    )


# ─── Revocación de API key ──────────────────────────────

@router.post("/me/api-keys/revoke", response_model=RevokeResponse)
def revoke_api_key(
    request: Request,
    developer: DeveloperAccount = Depends(get_current_developer),
    db: Session = Depends(get_auth_db),
):
    """Revoca inmediatamente todas las API keys activas del desarrollador.

    Después de revocar, será necesario contactar al administrador para obtener
    una nueva clave (o implementar un flujo de re-emisión en el futuro).
    """
    active_keys = crud.get_active_keys_for_developer(db, developer.id)
    if not active_keys:
        raise HTTPException(status_code=400, detail="No tienes claves activas para revocar")

    for key in active_keys:
        crud.revoke_api_key(db, key, immediate=True)

    client_ip = _get_client_ip(request)
    crud.create_audit_entry(
        db,
        developer_id=developer.id,
        event_type="key_revoked",
        ip_address=client_ip,
    )

    return RevokeResponse(message="Todas tus API keys han sido revocadas.")
