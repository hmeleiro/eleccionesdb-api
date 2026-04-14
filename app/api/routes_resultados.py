from typing import Optional

from fastapi import APIRouter, Depends, Query
from app.auth.dependencies import get_current_developer
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.pagination import PaginationParams, PaginatedResponse
from app.schemas.resultados import (
    TotalTerritorioSchema,
    VotoPartidoSchema,
    ResultadoCombinadoSchema,
)
from app import crud

router = APIRouter(prefix="/v1/resultados", tags=["Resultados"])


# ─── Totales territorio ─────────────────────────────────

@router.get("/totales-territorio", response_model=PaginatedResponse[TotalTerritorioSchema])
def list_totales_territorio(
    pagination: PaginationParams = Depends(),
    eleccion_id: Optional[list[int]] = Query(default=None, description="Filtrar por elección(es)"),
    territorio_id: Optional[list[int]] = Query(default=None, description="Filtrar por territorio(s)"),
    year: Optional[list[str]] = Query(default=None, description="Filtrar por año(s)"),
    tipo_eleccion: Optional[list[str]] = Query(default=None, description="Filtrar por tipo(s) de elección"),
    tipo_territorio: Optional[list[str]] = Query(default=None, description="Filtrar por tipo(s) de territorio"),
    codigo_ccaa: Optional[list[str]] = Query(default=None, description="Filtrar por código(s) CCAA"),
    codigo_provincia: Optional[list[str]] = Query(default=None, description="Filtrar por código(s) provincia"),
    codigo_municipio: Optional[list[str]] = Query(default=None, description="Filtrar por código(s) municipio"),
    db: Session = Depends(get_db),
    developer=Depends(get_current_developer),
):
    """Totales territorio (censo, participación, votos blancos/nulos…) con filtros."""
    return crud.get_totales_territorio(
        db,
        skip=pagination.skip,
        limit=pagination.limit,
        eleccion_id=eleccion_id,
        territorio_id=territorio_id,
        year=year,
        tipo_eleccion=tipo_eleccion,
        tipo_territorio=tipo_territorio,
        codigo_ccaa=codigo_ccaa,
        codigo_provincia=codigo_provincia,
        codigo_municipio=codigo_municipio,
    )


# ─── Votos partido ──────────────────────────────────────

@router.get("/votos-partido", response_model=PaginatedResponse[VotoPartidoSchema])
def list_votos_partido(
    pagination: PaginationParams = Depends(),
    eleccion_id: Optional[list[int]] = Query(default=None, description="Filtrar por elección(es)"),
    territorio_id: Optional[list[int]] = Query(default=None, description="Filtrar por territorio(s)"),
    partido_id: Optional[list[int]] = Query(default=None, description="Filtrar por partido(s)"),
    year: Optional[list[str]] = Query(default=None, description="Filtrar por año(s)"),
    tipo_eleccion: Optional[list[str]] = Query(default=None, description="Filtrar por tipo(s) de elección"),
    tipo_territorio: Optional[list[str]] = Query(default=None, description="Filtrar por tipo(s) de territorio"),
    codigo_ccaa: Optional[list[str]] = Query(default=None, description="Filtrar por código(s) CCAA"),
    codigo_provincia: Optional[list[str]] = Query(default=None, description="Filtrar por código(s) provincia"),
    codigo_municipio: Optional[list[str]] = Query(default=None, description="Filtrar por código(s) municipio"),
    db: Session = Depends(get_db),
    developer=Depends(get_current_developer),
):
    """Votos por partido y territorio con filtros opcionales."""
    return crud.get_votos_partido(
        db,
        skip=pagination.skip,
        limit=pagination.limit,
        eleccion_id=eleccion_id,
        territorio_id=territorio_id,
        partido_id=partido_id,
        year=year,
        tipo_eleccion=tipo_eleccion,
        tipo_territorio=tipo_territorio,
        codigo_ccaa=codigo_ccaa,
        codigo_provincia=codigo_provincia,
        codigo_municipio=codigo_municipio,
    )


# ─── Combinados: votos + partido recode + territorio + elección ─

@router.get("/combinados", response_model=PaginatedResponse[ResultadoCombinadoSchema])
def list_resultados_combinados(
    pagination: PaginationParams = Depends(),
    eleccion_id: Optional[list[int]] = Query(default=None, description="Filtrar por elección(es)"),
    territorio_id: Optional[list[int]] = Query(default=None, description="Filtrar por territorio(s)"),
    partido_id: Optional[list[int]] = Query(default=None, description="Filtrar por partido(s)"),
    year: Optional[list[str]] = Query(default=None, description="Filtrar por año(s)"),
    tipo_eleccion: Optional[list[str]] = Query(default=None, description="Filtrar por tipo(s) de elección"),
    tipo_territorio: Optional[list[str]] = Query(default=None, description="Filtrar por tipo(s) de territorio"),
    codigo_ccaa: Optional[list[str]] = Query(default=None, description="Filtrar por código(s) CCAA"),
    codigo_provincia: Optional[list[str]] = Query(default=None, description="Filtrar por código(s) provincia"),
    codigo_municipio: Optional[list[str]] = Query(default=None, description="Filtrar por código(s) municipio"),
    db: Session = Depends(get_db),
    developer=Depends(get_current_developer),
):
    """Votos con partido+recode, territorio y elección expandidos. Ideal para análisis cruzado."""
    return crud.get_resultados_combinados(
        db,
        skip=pagination.skip,
        limit=pagination.limit,
        eleccion_id=eleccion_id,
        territorio_id=territorio_id,
        partido_id=partido_id,
        year=year,
        tipo_eleccion=tipo_eleccion,
        tipo_territorio=tipo_territorio,
        codigo_ccaa=codigo_ccaa,
        codigo_provincia=codigo_provincia,
        codigo_municipio=codigo_municipio,
    )

