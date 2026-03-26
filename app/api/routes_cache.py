from fastapi import APIRouter

from app.cache import response_cache

router = APIRouter(prefix="/api/v1/cache", tags=["Cache"])


@router.get("/stats")
def cache_stats():
    """Estadísticas actuales de la caché en memoria (entradas, tamaño máximo, TTL)."""
    return response_cache.stats()


@router.post("/clear")
def cache_clear():
    """Limpia toda la caché en memoria."""
    response_cache.clear()
    return {"message": "Cache limpiada correctamente"}
