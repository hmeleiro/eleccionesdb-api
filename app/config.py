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
