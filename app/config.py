from pydantic_settings import BaseSettings
from pydantic import computed_field


class Settings(BaseSettings):
    """Configuración de la aplicación, leída de variables de entorno / .env"""

    # ── Base de datos ────────────────────────────────
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "eleccionesdb"
    DB_USER: str = "eleccionesdb_api"
    DB_PASSWORD: str = ""
    DB_SCHEMA: str = ""

    # ── Aplicación ───────────────────────────────────
    APP_ENV: str = "development"

    # root_path para funcionamiento detrás de Nginx reverse proxy.
    # Ejemplo: si Nginx sirve la API en /api → ROOT_PATH=/api
    ROOT_PATH: str = ""

    # ── Cache en memoria ─────────────────────────────
    CACHE_ENABLED: bool = True
    CACHE_TTL_CATALOGS: int = 86400     # 24 h — tipos de elección
    CACHE_TTL_REFERENCE: int = 3600     # 1 h  — elecciones, territorios, partidos
    CACHE_TTL_RESULTS: int = 3600       # 1 h  — resultados, combinados
    CACHE_MAX_CATALOGS: int = 64
    CACHE_MAX_REFERENCE: int = 512
    CACHE_MAX_RESULTS: int = 2048
    # ── Autenticación y API keys ─────────────────────────
    AUTH_DB_URL: str = "sqlite:///data/auth.db"

    # ── Resend (email transaccional) ─────────────────────
    RESEND_API_KEY: str = ""
    RESEND_FROM_EMAIL: str = "noreply@example.com"
    APP_BASE_URL: str = "http://localhost:8000"

    # ── Verificación y rate limiting ─────────────────────
    VERIFICATION_TOKEN_EXPIRY_HOURS: int = 24
    API_KEY_ROTATION_GRACE_HOURS: int = 1
    RATE_LIMIT_REGISTER_PER_IP: int = 5     # máx registros por IP/hora
    RATE_LIMIT_REGISTER_PER_EMAIL: int = 3  # máx intentos por email/hora

    # ── Panel de administrador ────────────────────────────
    ADMIN_EMAIL: str = ""
    ADMIN_PASSWORD: str = ""
    ADMIN_JWT_SECRET: str = "change-me-in-production"
    ADMIN_JWT_EXPIRE_HOURS: int = 8

    @computed_field  # type: ignore[prop-decorator]
    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()
