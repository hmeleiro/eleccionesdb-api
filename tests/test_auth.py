"""
Tests para el sistema de autenticación: registro, verificación y API keys.

Usa SQLite en memoria para la BD de auth. Mockea el servicio de email.
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.auth.database import AuthBase, AuthSessionLocal, auth_engine, get_auth_db
from app.auth.models import DeveloperAccount, ApiKey, EmailVerificationToken, AuditLog  # noqa: F401
from app.database import get_db
from app.main import app


# ─── Fixtures ────────────────────────────────────────────

# Override para la BD electoral (mock, no se usa en estos tests)
def _override_get_db():
    db = MagicMock()
    db.execute.return_value = None
    try:
        yield db
    finally:
        pass


# Motor SQLite en memoria para tests de auth
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

_test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@event.listens_for(_test_engine, "connect")
def _set_pragmas(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


_TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine)


def _override_get_auth_db():
    db = _TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Aplicar overrides
app.dependency_overrides[get_db] = _override_get_db
app.dependency_overrides[get_auth_db] = _override_get_auth_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def _setup_db():
    """Crea y destruye las tablas de auth antes/después de cada test."""
    AuthBase.metadata.create_all(bind=_test_engine)
    yield
    AuthBase.metadata.drop_all(bind=_test_engine)


# ─── Helpers ─────────────────────────────────────────────

def _register(email="test@example.com", name="Test User", **kwargs):
    """Helper para registrar un desarrollador."""
    payload = {"email": email, "name": name, **kwargs}
    return client.post("/v1/auth/register", json=payload)


def _activate_and_get_key(email="test@example.com", name="Test User"):
    """Registra, verifica y devuelve la API key completa."""
    from app.auth.service import generate_api_key, generate_verification_token, hash_token

    db = _TestSessionLocal()
    try:
        # Crear developer activo directamente
        from app.auth import crud

        dev = crud.create_developer(db, email=email, name=name)
        crud.activate_developer(db, dev)

        full_key, prefix, key_hash = generate_api_key()
        crud.create_api_key(db, developer_id=dev.id, key_prefix=prefix, key_hash=key_hash)
        return full_key, dev
    finally:
        db.close()


# ─── Tests de registro ──────────────────────────────────

@patch("app.api.routes_auth.email_service")
def test_register_new_developer(mock_email):
    """POST /v1/auth/register con datos válidos devuelve 201."""
    mock_email.send_verification_email.return_value = True
    response = _register()
    assert response.status_code == 201
    data = response.json()
    assert "developer_id" in data
    assert "message" in data


@patch("app.api.routes_auth.email_service")
def test_register_duplicate_active_email(mock_email):
    """Registrar dos veces el mismo email con cuenta activa devuelve 409."""
    mock_email.send_verification_email.return_value = True

    # Crear cuenta activa directamente
    _activate_and_get_key("dup@example.com")

    response = _register(email="dup@example.com", name="Dup")
    assert response.status_code == 409


@patch("app.api.routes_auth.email_service")
def test_register_duplicate_pending_email(mock_email):
    """Registrar dos veces el mismo email con cuenta pending devuelve 409."""
    mock_email.send_verification_email.return_value = True

    _register(email="pending@example.com", name="Pending")
    response = _register(email="pending@example.com", name="Pending 2")
    assert response.status_code == 409


# ─── Tests de verificación ──────────────────────────────

def test_verify_valid_token():
    """GET /v1/auth/verify con token válido activa la cuenta y devuelve HTML con API key."""
    from app.auth.service import generate_verification_token
    from app.auth import crud

    db = _TestSessionLocal()
    try:
        dev = crud.create_developer(db, email="verify@example.com", name="Verify")
        full_token, token_hash = generate_verification_token()
        expires = datetime.now(timezone.utc) + timedelta(hours=24)
        crud.create_verification_token(db, developer_id=dev.id, token_hash=token_hash, expires_at=expires)
    finally:
        db.close()

    response = client.get(f"/v1/auth/verify?token={full_token}")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Email verificado" in response.text
    # La API key debe estar presente en la respuesta HTML
    assert "X-API-Key" in response.text


def test_verify_expired_token():
    """GET /v1/auth/verify con token expirado devuelve error HTML."""
    from app.auth.service import generate_verification_token
    from app.auth import crud

    db = _TestSessionLocal()
    try:
        dev = crud.create_developer(db, email="expired@example.com", name="Expired")
        full_token, token_hash = generate_verification_token()
        # Token expirado hace 1 hora
        expires = datetime.now(timezone.utc) - timedelta(hours=1)
        crud.create_verification_token(db, developer_id=dev.id, token_hash=token_hash, expires_at=expires)
    finally:
        db.close()

    response = client.get(f"/v1/auth/verify?token={full_token}")
    assert response.status_code == 400
    assert "expirado" in response.text.lower() or "válido" in response.text.lower()


def test_verify_invalid_token():
    """GET /v1/auth/verify con token inválido devuelve error HTML."""
    response = client.get("/v1/auth/verify?token=tokentotalmenteinvalido")
    assert response.status_code == 400


# ─── Tests de autenticación por API key ─────────────────

def test_protected_endpoint_without_key():
    """Acceder a /v1/developers/me sin API key devuelve 401."""
    response = client.get("/v1/developers/me")
    assert response.status_code == 401


def test_protected_endpoint_with_invalid_key():
    """Acceder a /v1/developers/me con API key inválida devuelve 401."""
    response = client.get("/v1/developers/me", headers={"X-API-Key": "claveinvalida123"})
    assert response.status_code == 401


def test_protected_endpoint_with_valid_key():
    """Acceder a /v1/developers/me con API key válida devuelve 200."""
    full_key, dev = _activate_and_get_key("valid@example.com", "Valid")
    response = client.get("/v1/developers/me", headers={"X-API-Key": full_key})
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "valid@example.com"
    assert data["status"] == "active"


# ─── Tests de perfil ────────────────────────────────────

def test_developer_profile():
    """GET /v1/developers/me devuelve datos correctos del perfil."""
    full_key, dev = _activate_and_get_key("profile@example.com", "Profile User")
    response = client.get("/v1/developers/me", headers={"X-API-Key": full_key})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Profile User"
    assert data["api_key_prefix"] is not None
    assert len(data["api_key_prefix"]) == 8


# ─── Tests de rotación ──────────────────────────────────

def test_rotate_api_key():
    """POST /v1/developers/me/api-keys/rotate genera nueva clave."""
    full_key, dev = _activate_and_get_key("rotate@example.com", "Rotate")
    response = client.post(
        "/v1/developers/me/api-keys/rotate",
        headers={"X-API-Key": full_key},
    )
    assert response.status_code == 200
    data = response.json()
    assert "api_key" in data
    assert data["api_key"] != full_key
    assert len(data["key_prefix"]) == 8

    # La clave nueva debe funcionar
    new_key = data["api_key"]
    response2 = client.get("/v1/developers/me", headers={"X-API-Key": new_key})
    assert response2.status_code == 200

    # La clave antigua debe seguir funcionando (periodo de gracia)
    response3 = client.get("/v1/developers/me", headers={"X-API-Key": full_key})
    assert response3.status_code == 200


# ─── Tests de revocación ────────────────────────────────

def test_revoke_api_key():
    """POST /v1/developers/me/api-keys/revoke invalida la clave inmediatamente."""
    full_key, dev = _activate_and_get_key("revoke@example.com", "Revoke")

    response = client.post(
        "/v1/developers/me/api-keys/revoke",
        headers={"X-API-Key": full_key},
    )
    assert response.status_code == 200

    # La clave ya no debe funcionar
    response2 = client.get("/v1/developers/me", headers={"X-API-Key": full_key})
    assert response2.status_code == 401


# ─── Tests de reenvío de verificación ────────────────────

@patch("app.api.routes_auth.email_service")
def test_resend_verification_pending(mock_email):
    """POST /v1/auth/resend-verification para cuenta pending envía email."""
    mock_email.send_verification_email.return_value = True

    # Limpiar rate limiters para evitar contaminación entre tests
    from app.api.routes_auth import _ip_limiter, _email_limiter
    _ip_limiter._cache.clear()
    _email_limiter._cache.clear()

    # Registrar primero
    _register(email="resend@example.com", name="Resend")

    response = client.post(
        "/v1/auth/resend-verification",
        json={"email": "resend@example.com"},
    )
    assert response.status_code == 200
    assert "message" in response.json()


@patch("app.api.routes_auth.email_service")
def test_resend_verification_nonexistent(mock_email):
    """POST /v1/auth/resend-verification para email inexistente devuelve 200 (no filtra)."""
    from app.api.routes_auth import _ip_limiter
    _ip_limiter._cache.clear()

    response = client.post(
        "/v1/auth/resend-verification",
        json={"email": "noexiste@example.com"},
    )
    assert response.status_code == 200


# ─── Tests de rate limiting ──────────────────────────────

@patch("app.api.routes_auth.email_service")
def test_rate_limit_register(mock_email):
    """Superar el límite de registros por IP devuelve 429."""
    mock_email.send_verification_email.return_value = True

    # Reiniciar el rate limiter para tener un estado limpio
    from app.api.routes_auth import _ip_limiter
    _ip_limiter._cache.clear()

    # Enviar más registros que el límite (default 5)
    for i in range(5):
        client.post("/v1/auth/register", json={
            "email": f"ratelimit{i}@example.com",
            "name": f"RL {i}",
        })

    response = client.post("/v1/auth/register", json={
        "email": "ratelimit_extra@example.com",
        "name": "RL Extra",
    })
    assert response.status_code == 429


# ─── Tests de OpenAPI ────────────────────────────────────

def test_openapi_includes_auth_endpoints():
    """La documentación OpenAPI incluye los endpoints de auth."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    paths = schema["paths"]
    assert "/v1/auth/register" in paths
    assert "/v1/auth/verify" in paths
    assert "/v1/developers/me" in paths


def test_openapi_includes_api_key_security():
    """La documentación OpenAPI incluye el esquema de seguridad X-API-Key."""
    response = client.get("/openapi.json")
    schema = response.json()
    # Debe haber un securityScheme con APIKeyHeader
    security_schemes = schema.get("components", {}).get("securitySchemes", {})
    assert any(
        s.get("type") == "apiKey" and s.get("in") == "header" and s.get("name") == "X-API-Key"
        for s in security_schemes.values()
    ), f"No se encontró X-API-Key en securitySchemes: {security_schemes}"
