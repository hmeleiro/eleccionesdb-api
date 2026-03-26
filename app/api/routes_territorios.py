from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.pagination import PaginationParams, PaginatedResponse
from app.schemas.territorios import TerritorioList, TerritorioDetail
from app import crud

router = APIRouter(prefix="/api/v1", tags=["Territorios"])


@router.get("/territorios", response_model=PaginatedResponse[TerritorioList])
def list_territorios(
    pagination: PaginationParams = Depends(),
    tipo: Optional[list[str]] = Query(default=None, description="Filtrar por tipo (ccaa, provincia, municipio…). Acepta múltiples valores."),
    codigo_ccaa: Optional[list[str]] = Query(default=None, description="Filtrar por código(s) CCAA"),
    codigo_provincia: Optional[list[str]] = Query(default=None, description="Filtrar por código(s) provincia"),
    codigo_municipio: Optional[list[str]] = Query(default=None, description="Filtrar por código(s) municipio"),
    codigo_circunscripcion: Optional[list[str]] = Query(default=None, description="Filtrar por código(s) circunscripción"),
    nombre: Optional[str] = Query(default=None, description="Buscar por nombre (parcial, sin distinguir mayúsculas)"),
    db: Session = Depends(get_db),
):
    """Lista de territorios con filtros opcionales y paginación."""
    return crud.get_territorios(
        db,
        skip=pagination.skip,
        limit=pagination.limit,
        tipo=tipo,
        codigo_ccaa=codigo_ccaa,
        codigo_provincia=codigo_provincia,
        codigo_municipio=codigo_municipio,
        codigo_circunscripcion=codigo_circunscripcion,
        nombre=nombre,
    )


@router.get("/territorios/{territorio_id}", response_model=TerritorioDetail)
def get_territorio(territorio_id: int, db: Session = Depends(get_db)):
    """Detalle completo de un territorio con todos sus códigos."""
    obj = crud.get_territorio(db, territorio_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Territorio no encontrado")
    return obj


@router.get("/territorios/{territorio_id}/hijos", response_model=PaginatedResponse[TerritorioList])
def list_hijos_territorio(
    territorio_id: int,
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db),
):
    """Lista los hijos directos de un territorio (navegación jerárquica)."""
    parent = crud.get_territorio(db, territorio_id)
    if not parent:
        raise HTTPException(status_code=404, detail="Territorio padre no encontrado")
    return crud.get_hijos_territorio(
        db,
        territorio_id=territorio_id,
        skip=pagination.skip,
        limit=pagination.limit,
    )
