from fastapi import APIRouter, Depends
from app.auth.dependencies import get_current_developer

from app.cache import response_cache

router = APIRouter(prefix="/v1/cache", tags=["Cache"])


@router.get("/stats")
def cache_stats(developer=Depends(get_current_developer)):
    """Estadísticas actuales de la caché en memoria (entradas, tamaño máximo, TTL)."""
    return response_cache.stats()


@router.post("/clear")
def cache_clear(developer=Depends(get_current_developer)):
    """Limpia toda la caché en memoria."""
    response_cache.clear()
    return {"message": "Cache limpiada correctamente"}
