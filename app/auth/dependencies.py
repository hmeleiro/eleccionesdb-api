"""
Dependencias de seguridad para FastAPI:
- get_current_developer: autenticación por API key en header X-API-Key
- RateLimiter: limitación de tasa por clave (IP, email, etc.)
"""

import logging
from datetime import datetime, timezone

from cachetools import TTLCache
from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

from app.auth import crud
from app.auth.database import get_auth_db
from app.auth.models import DeveloperAccount
from app.auth.service import hash_token

logger = logging.getLogger("uvicorn.error")

# ─── Esquema de seguridad OpenAPI ────────────────────────

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


# ─── Autenticación por API Key ───────────────────────────

def get_current_developer(
    api_key: str | None = Security(api_key_header),
    db: Session = Depends(get_auth_db),
) -> DeveloperAccount:
    """Dependencia FastAPI: extrae y valida la API key del header X-API-Key.

    Devuelve el DeveloperAccount asociado, o lanza 401.
    """
    if not api_key:
        raise HTTPException(status_code=401, detail="API key requerida")

    key_hash = hash_token(api_key)
    db_key = crud.get_active_api_key_by_hash(db, key_hash)

    if not db_key:
        raise HTTPException(status_code=401, detail="API key inválida o revocada")

    developer = crud.get_developer_by_id(db, db_key.developer_id)
    if not developer or developer.status != "active":
        raise HTTPException(status_code=401, detail="Cuenta no activa")

    # Actualizar último uso (best-effort, no bloquear si falla)
    try:
        crud.update_last_used(db, db_key)
    except Exception:
        logger.warning("No se pudo actualizar last_used_at para key %s", db_key.key_prefix)

    return developer


# ─── Rate Limiter ────────────────────────────────────────

class RateLimiter:
    """Limitador de tasa simple basado en TTLCache.

    Cada clave (IP, email, etc.) tiene un contador que se reinicia tras `period` segundos.
    """

    def __init__(self, max_calls: int, period_seconds: int):
        self._max_calls = max_calls
        # maxsize alto para no perder entradas legítimas
        self._cache: TTLCache = TTLCache(maxsize=4096, ttl=period_seconds)

    def check(self, key: str) -> None:
        """Lanza HTTP 429 si la clave ha superado el límite."""
        count = self._cache.get(key, 0)
        if count >= self._max_calls:
            raise HTTPException(
                status_code=429,
                detail="Demasiadas solicitudes. Inténtalo más tarde.",
            )
        self._cache[key] = count + 1
