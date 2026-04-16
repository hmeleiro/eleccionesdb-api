"""
Servicios criptográficos para el panel de administración:
hashing de contraseñas (PBKDF2-HMAC-SHA256) y JWT.
"""

import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone

import jwt

from app.config import settings

_PBKDF2_ITERATIONS = 600_000
_PBKDF2_HASH = "sha256"
_SALT_BYTES = 32


def hash_password(password: str) -> str:
    """Devuelve 'salt$hash' usando PBKDF2-HMAC-SHA256."""
    salt = secrets.token_hex(_SALT_BYTES)
    dk = hashlib.pbkdf2_hmac(
        _PBKDF2_HASH,
        password.encode(),
        salt.encode(),
        _PBKDF2_ITERATIONS,
    )
    return f"{salt}${dk.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """Compara en tiempo constante la contraseña con el hash almacenado."""
    try:
        salt, stored_hash = stored.split("$", 1)
    except ValueError:
        return False
    dk = hashlib.pbkdf2_hmac(
        _PBKDF2_HASH,
        password.encode(),
        salt.encode(),
        _PBKDF2_ITERATIONS,
    )
    return hmac.compare_digest(dk.hex(), stored_hash)


def create_access_token(admin_id: int, email: str) -> str:
    """Genera un JWT firmado con ADMIN_JWT_SECRET."""
    expire = datetime.now(timezone.utc) + timedelta(hours=settings.ADMIN_JWT_EXPIRE_HOURS)
    payload = {
        "sub": str(admin_id),
        "email": email,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.ADMIN_JWT_SECRET, algorithm="HS256")


def decode_access_token(token: str) -> dict:
    """Decodifica y verifica el JWT. Lanza jwt.PyJWTError si es inválido."""
    return jwt.decode(token, settings.ADMIN_JWT_SECRET, algorithms=["HS256"])
