import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.config import settings
from app.api import (
    routes_health,
    routes_elecciones,
    routes_territorios,
    routes_partidos,
    routes_resultados,
    routes_cache,
    routes_auth,
    routes_developers,
)
from app.auth.database import init_auth_db

logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Elecciones DB API arrancando  [env=%s, cache=%s]", settings.APP_ENV, settings.CACHE_ENABLED)
    logger.info("Base de datos: %s@%s:%s/%s", settings.DB_USER, settings.DB_HOST, settings.DB_PORT, settings.DB_NAME)
    if settings.DB_SCHEMA:
        logger.info("Esquema BD: %s", settings.DB_SCHEMA)
    init_auth_db()
    yield
    logger.info("Elecciones DB API apagándose")


app = FastAPI(
    title="Elecciones DB API",
    description="API REST para consultar resultados electorales españoles.",
    version="1.0.0",
    root_path=settings.ROOT_PATH,
    lifespan=lifespan,
)

# ─── CORS ───────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://hmeleiro.github.io",
        "http://localhost:1313",
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# ─── Routers ────────────────────────────────────────────


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="./docs")


app.include_router(routes_health.router)
app.include_router(routes_elecciones.router)
app.include_router(routes_territorios.router)
app.include_router(routes_partidos.router)
app.include_router(routes_resultados.router)
app.include_router(routes_cache.router)
app.include_router(routes_auth.router)
app.include_router(routes_developers.router)

# ─── Cache middleware ───────────────────────────────────

if settings.CACHE_ENABLED:
    from app.cache import CacheMiddleware
    app.add_middleware(CacheMiddleware)
