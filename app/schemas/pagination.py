from typing import Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel

T = TypeVar("T")


class PaginationParams:
    """Parámetros de paginación reutilizables como dependency de FastAPI."""

    def __init__(
        self,
        skip: int = Query(default=0, ge=0, description="Registros a saltar"),
        limit: int = Query(default=50, ge=1, le=500, description="Máximo de registros a devolver"),
    ):
        self.skip = skip
        self.limit = limit


class PaginatedResponse(BaseModel, Generic[T]):
    """Respuesta paginada genérica con total de registros."""
    total: int
    skip: int
    limit: int
    data: list[T]
