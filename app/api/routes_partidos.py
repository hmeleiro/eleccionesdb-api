from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.pagination import PaginationParams, PaginatedResponse
from app.schemas.partidos import (
    PartidoList,
    PartidoDetail,
    PartidoRecodeSchema,
    PartidoRecodeDetail,
)
from app import crud

router = APIRouter(prefix="/v1", tags=["Partidos"])


# ─── Partidos ───────────────────────────────────────────

@router.get("/partidos", response_model=PaginatedResponse[PartidoList])
def list_partidos(
    pagination: PaginationParams = Depends(),
    siglas: Optional[str] = Query(default=None, description="Buscar por siglas (parcial, sin distinguir mayúsculas)"),
    db: Session = Depends(get_db),
):
    """Lista de partidos con filtro opcional por siglas y paginación."""
    return crud.get_partidos(
        db,
        skip=pagination.skip,
        limit=pagination.limit,
        siglas=siglas,
    )


@router.get("/partidos/{partido_id}", response_model=PartidoDetail)
def get_partido(partido_id: int, db: Session = Depends(get_db)):
    """Detalle de un partido con su recode/agrupación expandida."""
    obj = crud.get_partido(db, partido_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Partido no encontrado")
    return obj


# ─── Partidos recode (agrupaciones) ─────────────────────

@router.get("/partidos-recode", response_model=PaginatedResponse[PartidoRecodeSchema])
def list_partidos_recode(
    pagination: PaginationParams = Depends(),
    agrupacion: Optional[str] = Query(default=None, description="Filtrar por agrupación (parcial)"),
    db: Session = Depends(get_db),
):
    """Lista de agrupaciones de partidos (recodes) con paginación."""
    return crud.get_partidos_recode(
        db,
        skip=pagination.skip,
        limit=pagination.limit,
        agrupacion=agrupacion,
    )


@router.get("/partidos-recode/{partido_recode_id}", response_model=PartidoRecodeDetail)
def get_partido_recode(partido_recode_id: int, db: Session = Depends(get_db)):
    """Detalle de una agrupación con la lista de partidos asociados."""
    obj = crud.get_partido_recode(db, partido_recode_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Partido recode no encontrado")
    return obj
