"""
Caché en memoria para respuestas HTTP usando cachetools.

Las respuestas JSON se cachean organizadas en tiers con distintos TTL
y tamaños máximos según la categoría del endpoint.  Ideal para datos
inmutables como resultados electorales históricos.
"""

import logging
import threading
from urllib.parse import parse_qsl, urlencode

from cachetools import TTLCache
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.config import settings

logger = logging.getLogger("uvicorn.error")


# ─────────────────────────────────────────────────────────
# Cache manager
# ─────────────────────────────────────────────────────────

class ResponseCache:
    """Caché de respuestas HTTP con TTL por tier."""

    def __init__(self):
        self._lock = threading.Lock()
        self._tiers: dict[str, TTLCache] = {
            "catalogs": TTLCache(
                maxsize=settings.CACHE_MAX_CATALOGS,
                ttl=settings.CACHE_TTL_CATALOGS,
            ),
            "reference": TTLCache(
                maxsize=settings.CACHE_MAX_REFERENCE,
                ttl=settings.CACHE_TTL_REFERENCE,
            ),
            "results": TTLCache(
                maxsize=settings.CACHE_MAX_RESULTS,
                ttl=settings.CACHE_TTL_RESULTS,
            ),
        }
        # Orden importa: prefijos más específicos primero
        self._path_rules: list[tuple[str, str]] = [
            ("/v1/tipos-eleccion", "catalogs"),
            ("/v1/resultados", "results"),
            ("/v1/elecciones", "reference"),
            ("/v1/territorios", "reference"),
            ("/v1/partidos", "reference"),
        ]

    def _resolve_tier(self, path: str) -> str | None:
        for prefix, tier in self._path_rules:
            if path.startswith(prefix):
                return tier
        return None

    @staticmethod
    def _normalize_query(query_string: str) -> str:
        """Ordena los parámetros para generar claves de caché consistentes."""
        params = parse_qsl(query_string, keep_blank_values=True)
        return urlencode(sorted(params))

    def get(self, path: str, query_string: str) -> tuple[bytes, str] | None:
        tier_name = self._resolve_tier(path)
        if tier_name is None:
            return None
        key = f"{path}?{self._normalize_query(query_string)}"
        with self._lock:
            return self._tiers[tier_name].get(key)

    def set(self, path: str, query_string: str, value: tuple[bytes, str]):
        tier_name = self._resolve_tier(path)
        if tier_name is None:
            return
        key = f"{path}?{self._normalize_query(query_string)}"
        with self._lock:
            self._tiers[tier_name][key] = value

    def clear(self):
        with self._lock:
            for cache in self._tiers.values():
                cache.clear()
        logger.info("Cache limpiada")

    def stats(self) -> dict:
        with self._lock:
            return {
                name: {
                    "entries": cache.currsize,
                    "maxsize": cache.maxsize,
                    "ttl_seconds": int(cache.ttl),
                }
                for name, cache in self._tiers.items()
            }


response_cache = ResponseCache()


# ─────────────────────────────────────────────────────────
# Middleware
# ─────────────────────────────────────────────────────────

class CacheMiddleware(BaseHTTPMiddleware):
    """Middleware que cachea respuestas GET exitosas en memoria."""

    async def dispatch(self, request: Request, call_next):
        if request.method != "GET":
            return await call_next(request)

        path = request.scope["path"]
        query_string = request.scope.get("query_string", b"").decode()

        # Solo cachear rutas que pertenecen a un tier
        if response_cache._resolve_tier(path) is None:
            return await call_next(request)

        # ¿Está en caché?
        cached = response_cache.get(path, query_string)
        if cached is not None:
            body, content_type = cached
            return Response(
                content=body,
                media_type=content_type,
                headers={"X-Cache": "HIT"},
            )

        # Ejecutar handler
        response = await call_next(request)

        # Solo cachear respuestas 200
        if response.status_code == 200:
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            content_type = response.headers.get("content-type", "application/json")
            response_cache.set(path, query_string, (body, content_type))
            return Response(
                content=body,
                status_code=200,
                media_type=content_type,
                headers={"X-Cache": "MISS"},
            )

        return response
