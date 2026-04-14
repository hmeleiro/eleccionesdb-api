"""
Operaciones criptográficas para API keys y tokens de verificación.

Usa stdlib exclusivamente: secrets para generación, hashlib/hmac para hashing.
"""

import hashlib
import hmac
import secrets


def generate_api_key() -> tuple[str, str, str]:
    """Genera una API key criptográficamente segura.

    Returns:
        (full_key, prefix, key_hash)
        - full_key:  clave completa para entregar al usuario (una sola vez)
        - prefix:    primeros 8 caracteres (visible en BD para identificación)
        - key_hash:  SHA-256 hex de la clave completa (se almacena en BD)
    """
    full_key = secrets.token_urlsafe(32)
    prefix = full_key[:8]
    key_hash = hashlib.sha256(full_key.encode()).hexdigest()
    return full_key, prefix, key_hash


def generate_verification_token() -> tuple[str, str]:
    """Genera un token de verificación de email.

    Returns:
        (full_token, token_hash)
        - full_token: token completo para incluir en el enlace de verificación
        - token_hash: SHA-256 hex del token (se almacena en BD)
    """
    full_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(full_token.encode()).hexdigest()
    return full_token, token_hash


def hash_token(token: str) -> str:
    """Calcula el SHA-256 hex de un token en claro."""
    return hashlib.sha256(token.encode()).hexdigest()


def verify_key(plain_key: str, stored_hash: str) -> bool:
    """Compara una clave en claro con su hash almacenado (constant-time)."""
    computed = hashlib.sha256(plain_key.encode()).hexdigest()
    return hmac.compare_digest(computed, stored_hash)
