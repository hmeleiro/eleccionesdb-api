from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.pagination import PaginationParams, PaginatedResponse
from app.schemas.elecciones import TipoEleccionSchema, EleccionList, EleccionDetail
from app.schemas.resultados import TotalTerritorioSchema, ResultadoCompletoSchema
from app import crud

router = APIRouter(prefix="/api/v1", tags=["Elecciones"])


# ─── Tipos de elección ──────────────────────────────────

@router.get("/tipos-eleccion", response_model=list[TipoEleccionSchema])
def list_tipos_eleccion(db: Session = Depends(get_db)):
    """Lista todos los tipos de elección (catálogo pequeño, sin paginación)."""
    return crud.get_tipos_eleccion(db)


@router.get("/tipos-eleccion/{codigo}", response_model=TipoEleccionSchema)
def get_tipo_eleccion(codigo: str, db: Session = Depends(get_db)):
    """Detalle de un tipo de elección por su código."""
    obj = crud.get_tipo_eleccion(db, codigo)
    if not obj:
        raise HTTPException(status_code=404, detail="Tipo de elección no encontrado")
    return obj


# ─── Elecciones ─────────────────────────────────────────

@router.get("/elecciones", response_model=PaginatedResponse[EleccionList])
def list_elecciones(
    pagination: PaginationParams = Depends(),
    tipo_eleccion: Optional[list[str]] = Query(default=None, description="Filtrar por tipo (G, A, M, E…). Acepta múltiples valores."),
    year: Optional[list[str]] = Query(default=None, description="Filtrar por año (4 dígitos). Acepta múltiples valores."),
    ambito: Optional[list[str]] = Query(default=None, description="Filtrar por ámbito. Acepta múltiples valores."),
    db: Session = Depends(get_db),
):
    """Lista de elecciones con filtros opcionales y paginación."""
    return crud.get_elecciones(
        db,
        skip=pagination.skip,
        limit=pagination.limit,
        tipo_eleccion=tipo_eleccion,
        year=year,
        ambito=ambito,
    )


@router.get("/elecciones/{eleccion_id}", response_model=EleccionDetail)
def get_eleccion(eleccion_id: int, db: Session = Depends(get_db)):
    """Detalle completo de una elección con tipo expandido."""
    obj = crud.get_eleccion(db, eleccion_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Elección no encontrada")
    return obj


# ─── Totales territorio por elección ────────────────────

@router.get(
    "/elecciones/{eleccion_id}/totales-territorio",
    response_model=PaginatedResponse[TotalTerritorioSchema],
)
def list_totales_territorio_eleccion(
    eleccion_id: int,
    pagination: PaginationParams = Depends(),
    territorio_id: Optional[list[int]] = Query(default=None, description="Filtrar por territorio(s)"),
    tipo_territorio: Optional[list[str]] = Query(default=None, description="Filtrar por tipo de territorio (ccaa, provincia, municipio…)"),
    codigo_ccaa: Optional[list[str]] = Query(default=None, description="Filtrar por código(s) CCAA"),
    codigo_provincia: Optional[list[str]] = Query(default=None, description="Filtrar por código(s) provincia"),
    codigo_municipio: Optional[list[str]] = Query(default=None, description="Filtrar por código(s) municipio"),
    db: Session = Depends(get_db),
):
    """Totales territorio de una elección concreta, con filtros opcionales."""
    return crud.get_totales_territorio_eleccion(
        db,
        eleccion_id=eleccion_id,
        skip=pagination.skip,
        limit=pagination.limit,
        territorio_id=territorio_id,
        tipo_territorio=tipo_territorio,
        codigo_ccaa=codigo_ccaa,
        codigo_provincia=codigo_provincia,
        codigo_municipio=codigo_municipio,
    )


@router.get(
    "/elecciones/{eleccion_id}/totales-territorio/{territorio_id}",
    response_model=ResultadoCompletoSchema,
)
def get_resultado_completo(
    eleccion_id: int,
    territorio_id: int,
    db: Session = Depends(get_db),
):
    """Resultado completo: totales territorio + desglose de votos por partido."""
    resultado = crud.get_resultado_completo(db, eleccion_id, territorio_id)
    if resultado["totales_territorio"] is None and not resultado["votos_partido"]:
        raise HTTPException(
            status_code=404,
            detail="No se encontraron resultados para esta elección y territorio",
        )
    return resultado
