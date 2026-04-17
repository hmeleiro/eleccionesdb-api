import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.config import settings
from fastapi.staticfiles import StaticFiles

from app.api import (
    routes_health,
    routes_elecciones,
    routes_territorios,
    routes_partidos,
    routes_resultados,
    routes_cache,
    routes_auth,
    routes_developers,
    routes_admin,
)
from app.auth.database import init_auth_db, init_admin_user

logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Elecciones DB API arrancando  [env=%s, cache=%s]", settings.APP_ENV, settings.CACHE_ENABLED)
    if settings.ADMIN_JWT_SECRET == "change-me-in-production" and settings.APP_ENV != "development":
        logger.warning(
            "\u26a0 ADMIN_JWT_SECRET tiene el valor por defecto. "
            "Cámbialo en producción para garantizar la seguridad del panel de administración."
        )
    logger.info("Base de datos: %s@%s:%s/%s", settings.DB_USER, settings.DB_HOST, settings.DB_PORT, settings.DB_NAME)
    if settings.DB_SCHEMA:
        logger.info("Esquema BD: %s", settings.DB_SCHEMA)
    init_auth_db()
    init_admin_user()
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
    allow_origins=settings.FRONTEND_ORIGINS,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["*"],
)


# ─── Security headers ──────────────────────────────────

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    return response

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
app.include_router(routes_admin.router)

# ─── Cache middleware ───────────────────────────────────

if settings.CACHE_ENABLED:
    from app.cache import CacheMiddleware
    app.add_middleware(CacheMiddleware)
