from fastapi import Request

def _get_client_ip(request: Request) -> str:
    """Obtiene la IP del cliente, respetando X-Forwarded-For si existe."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"
from app.auth.schemas import (
    RegisterRequest,
    RegisterResponse,
    ResendVerificationRequest,
    ResendVerificationResponse,
    RecoverAccessRequest,
    RecoverAccessResponse,
    RestoreSessionResponse,
)

import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from fastapi import Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.auth import crud
from app.auth.database import get_auth_db
from app.auth.dependencies import RateLimiter
from app.auth.schemas import (
    RegisterRequest,
    RegisterResponse,
    ResendVerificationRequest,
    ResendVerificationResponse,
    RecoverAccessRequest,
    RecoverAccessResponse,
    RestoreSessionResponse,
)
from app.auth.service import generate_api_key, generate_verification_token, hash_token
from app.config import settings
from app.services.email import email_service
import secrets

logger = logging.getLogger("uvicorn.error")

router = APIRouter(prefix="/v1/auth", tags=["Autenticación"])

_ip_limiter = RateLimiter(max_calls=5, period_seconds=60)
_email_limiter = RateLimiter(max_calls=3, period_seconds=60)

_RECOVER_ACCESS_TOKEN_EXPIRY_HOURS = 1

def _build_restore_session_url(token: str) -> str:
    base = settings.APP_BASE_URL.rstrip("/")
    root = settings.ROOT_PATH.rstrip("/")
    return f"{base}{root}/v1/auth/restore-session?token={token}"

@router.post("/recover-access", response_model=RecoverAccessResponse, include_in_schema=True)
def recover_access(
    body: RecoverAccessRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_auth_db),
):
    """Permite recuperar acceso si el usuario ha perdido todas sus API keys."""
    generic_message = "Si el email está registrado y activo, recibirás un enlace para restaurar el acceso."
    developer = crud.get_developer_by_email(db, body.email.lower())
    if not developer or developer.status != "active":
        return RecoverAccessResponse(message=generic_message)

    # Generar token de acceso temporal (reutilizamos EmailVerificationToken)
    full_token, token_hash = generate_verification_token()
    expires_at = datetime.now(timezone.utc) + timedelta(hours=_RECOVER_ACCESS_TOKEN_EXPIRY_HOURS)
    crud.create_verification_token(
        db,
        developer_id=developer.id,
        token_hash=token_hash,
        expires_at=expires_at,
    )

    restore_url = _build_restore_session_url(full_token)
    # Reutilizamos el email de verificación pero con otro texto
    background_tasks.add_task(
        email_service.send_verification_email,
        developer.email,
        developer.name,
        restore_url,
    )

    crud.create_audit_entry(
        db,
        developer_id=developer.id,
        event_type="recover_access",
    )

    return RecoverAccessResponse(message=generic_message)


@router.get("/restore-session", response_model=RestoreSessionResponse, response_class=HTMLResponse, include_in_schema=True)
def restore_session(
    token: str,
    request: Request,
    db: Session = Depends(get_auth_db),
):
    """Permite restaurar sesión y generar una nueva API key usando un enlace temporal enviado por email."""
    token_hash = hash_token(token)
    db_token = crud.get_valid_verification_token(db, token_hash)
    if not db_token:
        return HTMLResponse(
            content=_VERIFY_ERROR_HTML.format(
                message="El enlace de restauración no es válido o ha expirado."
            ),
            status_code=400,
        )
    developer = crud.get_developer_by_id(db, db_token.developer_id)
    if not developer or developer.status != "active":
        return HTMLResponse(
            content=_VERIFY_ERROR_HTML.format(message="Cuenta no encontrada o inactiva."),
            status_code=400,
        )
    # Marcar token como usado
    crud.mark_token_used(db, db_token)
    # Generar nueva API key
    full_key, prefix, key_hash = generate_api_key()
    crud.create_api_key(
        db,
        developer_id=developer.id,
        key_prefix=prefix,
        key_hash=key_hash,
        label="recovery",
    )
    client_ip = _get_client_ip(request)
    crud.create_audit_entry(
        db,
        developer_id=developer.id,
        event_type="key_created_recovery",
        ip_address=client_ip,
        details=f"prefix={prefix}",
    )
    base_url = settings.APP_BASE_URL.rstrip("/")
    html = _VERIFY_HTML_TEMPLATE.format(api_key=full_key, base_url=base_url)
    return HTMLResponse(content=html, status_code=200)


# ─── Registro ────────────────────────────────────────────

@router.post("/register", response_model=RegisterResponse, status_code=201)
def register(
    body: RegisterRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_auth_db),
):
    """Registra una nueva cuenta de desarrollador.

    Genera un token de verificación y envía un email con el enlace.
    La cuenta queda en estado 'pending' hasta verificar el email.
    """
    client_ip = _get_client_ip(request)

    # Rate limit por IP
    _ip_limiter.check(client_ip)

    # TODO: CAPTCHA integration point
    # Aquí se validaría un token CAPTCHA (reCAPTCHA, hCaptcha, Turnstile, etc.)
    # antes de proceder con el registro.

    # Rate limit por email
    _email_limiter.check(body.email.lower())

    # Verificar email no duplicado
    existing = crud.get_developer_by_email(db, body.email.lower())
    if existing:
        if existing.status == "active":
            raise HTTPException(
                status_code=409,
                detail="Ya existe una cuenta activa con este email",
            )
        if existing.status == "pending":
            raise HTTPException(
                status_code=409,
                detail="Ya existe un registro pendiente de verificación con este email. Usa el endpoint de reenvío.",
            )

    # Crear cuenta
    developer = crud.create_developer(
        db,
        email=body.email.lower(),
        name=body.name,
        organization=body.organization,
        intended_use=body.intended_use,
    )

    # Generar token de verificación
    full_token, token_hash = generate_verification_token()
    expires_at = datetime.now(timezone.utc) + timedelta(hours=settings.VERIFICATION_TOKEN_EXPIRY_HOURS)
    crud.create_verification_token(
        db,
        developer_id=developer.id,
        token_hash=token_hash,
        expires_at=expires_at,
    )

    # Enviar email en background
    verification_url = _build_verification_url(full_token)
    background_tasks.add_task(
        _send_verification_email_task,
        developer.email,
        developer.name,
        verification_url,
    )

    # Auditoría
    crud.create_audit_entry(
        db,
        developer_id=developer.id,
        event_type="registration",
        ip_address=client_ip,
    )

    return RegisterResponse(
        message="Registro recibido. Revisa tu email para verificar tu cuenta.",
        developer_id=developer.id,
    )


# ─── Verificación ────────────────────────────────────────


_VERIFY_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang='es'>
<head>
    <meta charset='utf-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1'>
    <title>Verificación — Spain Electoral Project</title>
    <style>
        body {{
            background: #fafbfc;
            font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            color: #1a1a2e;
            max-width: 560px;
            margin: 0 auto;
            padding: 40px 0;
            line-height: 1.6;
        }}
        .container {{
            background: #fff;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            border: 1px solid #e5e7eb;
            padding: 2.5rem 2rem 2rem 2rem;
            margin: 0 auto;
        }}
        h1 {{ font-size: 2rem; color: #2d5bff; margin-bottom: 1.5rem; font-weight: 700; }}
        h2 {{ font-size: 1.25rem; color: #1a1a2e; margin-bottom: 1rem; font-weight: 600; }}
        p {{ font-size: 1rem; color: #1a1a2e; margin: 0.5rem 0 1.25rem 0; }}
        .key-box {{ background: #f1f5ff; border: 1px solid #2d5bff33; border-radius: 8px; padding: 18px; font-family: monospace; font-size: 1.1rem; word-break: break-all; margin: 18px 0; color: #2d5bff; }}
        .warning {{ background: #fef3c7; border: 1px solid #f59e0b; border-radius: 6px; padding: 12px; font-size: 0.98rem; margin: 18px 0; color: #7a5a00; }}
        .footer {{ color: #9ca3af; font-size: 0.875rem; margin-top: 2.5rem; text-align: center; }}
        pre {{ background: #f8fafc; padding: 12px; border-radius: 6px; overflow-x: auto; font-size: 0.98rem; }}
    </style>
</head>
<body>
    <div class='container'>
        <h1>Email verificado</h1>
        <p>Tu cuenta ha sido activada correctamente.</p>
        <h2>Tu API Key</h2>
        <div class='key-box'>{api_key}</div>
        <div class='warning'>
            <strong>&#9888; Importante:</strong> Esta es la única vez que se mostrará la clave completa.<br>
            Cópiala y guárdala en un lugar seguro.
        </div>
        <h2>Cómo usarla</h2>
        <p>Incluye la clave en el header <code>X-API-Key</code> de tus peticiones:</p>
        <pre>curl -H "X-API-Key: {api_key}" {base_url}/v1/elecciones</pre>
        <div class='footer'>Spain Electoral Project &mdash; API</div>
    </div>
</body>
</html>"""


_VERIFY_ERROR_HTML = """\
<!DOCTYPE html>
<html lang='es'>
<head>
    <meta charset='utf-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1'>
    <title>Verificación fallida — Spain Electoral Project</title>
    <style>
        body {{
            background: #fafbfc;
            font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            color: #1a1a2e;
            max-width: 560px;
            margin: 0 auto;
            padding: 40px 0;
            line-height: 1.6;
        }}
        .container {{
            background: #fff;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            border: 1px solid #e5e7eb;
            padding: 2.5rem 2rem 2rem 2rem;
            margin: 0 auto;
        }}
        h1 {{ font-size: 2rem; color: #b91c1c; margin-bottom: 1.5rem; font-weight: 700; }}
        p {{ font-size: 1.1rem; color: #1a1a2e; margin-bottom: 1.5rem; }}
        .footer {{ color: #9ca3af; font-size: 0.875rem; margin-top: 2.5rem; text-align: center; }}
    </style>
</head>
<body>
    <div class='container'>
        <h1>Verificación fallida</h1>
        <p>{message}</p>
        <p>Si crees que es un error, solicita un nuevo enlace de verificación.</p>
        <div class='footer'>Spain Electoral Project &mdash; API</div>
    </div>
</body>
</html>"""


@router.get("/verify", include_in_schema=True)
def verify_email(
    token: str,
    request: Request,
    db: Session = Depends(get_auth_db),
):
    """Verifica el email del desarrollador y emite la primera API key.

    Se accede desde el enlace del email. Devuelve HTML con la API key.
    """
    from fastapi.responses import HTMLResponse

    token_hash = hash_token(token)
    db_token = crud.get_valid_verification_token(db, token_hash)

    if not db_token:
        return HTMLResponse(
            content=_VERIFY_ERROR_HTML.format(
                message="El enlace de verificación no es válido o ha expirado."
            ),
            status_code=400,
        )

    developer = crud.get_developer_by_id(db, db_token.developer_id)
    if not developer:
        return HTMLResponse(
            content=_VERIFY_ERROR_HTML.format(message="Cuenta no encontrada."),
            status_code=400,
        )

    if developer.status == "active" and developer.email_verified:
        return HTMLResponse(
            content=_VERIFY_ERROR_HTML.format(
                message="Esta cuenta ya ha sido verificada."
            ),
            status_code=400,
        )

    # Marcar token como usado y activar cuenta
    crud.mark_token_used(db, db_token)
    crud.activate_developer(db, developer)

    # Generar primera API key
    full_key, prefix, key_hash = generate_api_key()
    crud.create_api_key(
        db,
        developer_id=developer.id,
        key_prefix=prefix,
        key_hash=key_hash,
        label="default",
    )

    client_ip = _get_client_ip(request)
    crud.create_audit_entry(
        db,
        developer_id=developer.id,
        event_type="verification",
        ip_address=client_ip,
    )
    crud.create_audit_entry(
        db,
        developer_id=developer.id,
        event_type="key_created",
        ip_address=client_ip,
        details=f"prefix={prefix}",
    )

    base_url = settings.APP_BASE_URL.rstrip("/")
    return HTMLResponse(
        content=_VERIFY_HTML_TEMPLATE.format(api_key=full_key, base_url=base_url),
        status_code=200,
    )


# ─── Reenvío de verificación ─────────────────────────────

@router.post("/resend-verification", response_model=ResendVerificationResponse)
def resend_verification(
    body: ResendVerificationRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_auth_db),
):
    """Solicita reenvío del email de verificación.

    Solo funciona para cuentas en estado 'pending'.
    Respuesta genérica para no filtrar si el email existe.
    """
    client_ip = _get_client_ip(request)
    _ip_limiter.check(client_ip)

    generic_message = "Si el email está registrado y pendiente de verificación, recibirás un nuevo enlace."

    developer = crud.get_developer_by_email(db, body.email.lower())
    if not developer or developer.status != "pending":
        return ResendVerificationResponse(message=generic_message)

    # Cooldown: no reenviar si el último token se creó hace menos de 2 minutos
    last_created = crud.get_latest_token_created_at(db, developer.id)
    if last_created:
        # Asegurar que last_created tenga tzinfo
        if last_created.tzinfo is None:
            last_created = last_created.replace(tzinfo=timezone.utc)
        elapsed = (datetime.now(timezone.utc) - last_created).total_seconds()
        if elapsed < _RESEND_COOLDOWN_SECONDS:
            return ResendVerificationResponse(message=generic_message)

    # Generar nuevo token
    full_token, token_hash = generate_verification_token()
    expires_at = datetime.now(timezone.utc) + timedelta(hours=settings.VERIFICATION_TOKEN_EXPIRY_HOURS)
    crud.create_verification_token(
        db,
        developer_id=developer.id,
        token_hash=token_hash,
        expires_at=expires_at,
    )

    # Enviar en background
    verification_url = _build_verification_url(full_token)
    background_tasks.add_task(
        _send_verification_email_task,
        developer.email,
        developer.name,
        verification_url,
    )

    crud.create_audit_entry(
        db,
        developer_id=developer.id,
        event_type="resend_verification",
        ip_address=client_ip,
    )

    return ResendVerificationResponse(message=generic_message)
