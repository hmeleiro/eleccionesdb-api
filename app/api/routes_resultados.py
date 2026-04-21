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
    TotalTerritorioSearch,
    VotoPartidoSearch,
    ResultadoCombinadoSearch,
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
    """Totales territorio (censo, participación, votos blancos/nulos…) con filtros.

    Usa este endpoint GET para consultas sencillas con pocos identificadores.
    Si necesitas filtrar por listas largas de municipios u otros identificadores,
    usa **POST /v1/resultados/totales-territorio** con los filtros en el cuerpo JSON
    para evitar errores `414 URI Too Long`.
    """
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


@router.post(
    "/totales-territorio",
    response_model=PaginatedResponse[TotalTerritorioSchema],
    summary="Buscar totales territorio con filtros complejos (body JSON)",
)
def search_totales_territorio(
    body: TotalTerritorioSearch,
    db: Session = Depends(get_db),
    developer=Depends(get_current_developer),
):
    """Totales territorio (censo, participación, votos blancos/nulos…) con filtros en body JSON.

    Endpoint de **solo lectura**. Equivale al GET, pero acepta los filtros en el cuerpo JSON
    en lugar de query parameters. Úsalo cuando necesites listas largas de municipios u otros
    identificadores que provocarían errores `414 URI Too Long` en el GET.

    Ejemplo de body:
    ```json
    {
      "paginacion": {"skip": 0, "limit": 100},
      "year": ["2019", "2023"],
      "tipo_eleccion": ["G"],
      "codigo_municipio": ["28001", "28002", "28003"]
    }
    ```
    """
    return crud.get_totales_territorio(
        db,
        skip=body.paginacion.skip,
        limit=body.paginacion.limit,
        eleccion_id=body.eleccion_id,
        territorio_id=body.territorio_id,
        year=body.year,
        tipo_eleccion=body.tipo_eleccion,
        tipo_territorio=body.tipo_territorio,
        codigo_ccaa=body.codigo_ccaa,
        codigo_provincia=body.codigo_provincia,
        codigo_municipio=body.codigo_municipio,
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
    """Votos por partido y territorio con filtros opcionales.

    Usa este endpoint GET para consultas sencillas con pocos identificadores.
    Si necesitas filtrar por listas largas de municipios u otros identificadores,
    usa **POST /v1/resultados/votos-partido** con los filtros en el cuerpo JSON
    para evitar errores `414 URI Too Long`.
    """
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


@router.post(
    "/votos-partido",
    response_model=PaginatedResponse[VotoPartidoSchema],
    summary="Buscar votos por partido con filtros complejos (body JSON)",
)
def search_votos_partido(
    body: VotoPartidoSearch,
    db: Session = Depends(get_db),
    developer=Depends(get_current_developer),
):
    """Votos por partido y territorio con filtros en body JSON.

    Endpoint de **solo lectura**. Equivale al GET, pero acepta los filtros en el cuerpo JSON
    en lugar de query parameters. Úsalo cuando necesites listas largas de municipios u otros
    identificadores que provocarían errores `414 URI Too Long` en el GET.

    Ejemplo de body:
    ```json
    {
      "paginacion": {"skip": 0, "limit": 100},
      "year": ["2023"],
      "tipo_eleccion": ["G"],
      "partido_id": [1, 2, 3],
      "codigo_municipio": ["28001", "28002", "28003"]
    }
    ```
    """
    return crud.get_votos_partido(
        db,
        skip=body.paginacion.skip,
        limit=body.paginacion.limit,
        eleccion_id=body.eleccion_id,
        territorio_id=body.territorio_id,
        partido_id=body.partido_id,
        year=body.year,
        tipo_eleccion=body.tipo_eleccion,
        tipo_territorio=body.tipo_territorio,
        codigo_ccaa=body.codigo_ccaa,
        codigo_provincia=body.codigo_provincia,
        codigo_municipio=body.codigo_municipio,
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
    """Votos con partido+recode, territorio y elección expandidos. Ideal para análisis cruzado.

    Usa este endpoint GET para consultas sencillas con pocos identificadores.
    Si necesitas filtrar por listas largas de municipios u otros identificadores,
    usa **POST /v1/resultados/combinados** con los filtros en el cuerpo JSON
    para evitar errores `414 URI Too Long`.
    """
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


@router.post(
    "/combinados",
    response_model=PaginatedResponse[ResultadoCombinadoSchema],
    summary="Buscar resultados combinados con filtros complejos (body JSON)",
)
def search_resultados_combinados(
    body: ResultadoCombinadoSearch,
    db: Session = Depends(get_db),
    developer=Depends(get_current_developer),
):
    """Votos con partido+recode, territorio y elección expandidos, con filtros en body JSON.

    Endpoint de **solo lectura**. Equivale al GET, pero acepta los filtros en el cuerpo JSON
    en lugar de query parameters. Úsalo cuando necesites listas largas de municipios u otros
    identificadores que provocarían errores `414 URI Too Long` en el GET.

    Ejemplo de body:
    ```json
    {
      "paginacion": {"skip": 0, "limit": 200},
      "year": ["2023"],
      "tipo_eleccion": ["G"],
      "tipo_territorio": ["municipio"],
      "codigo_municipio": ["28001", "28002", "28003", "08001"]
    }
    ```
    """
    return crud.get_resultados_combinados(
        db,
        skip=body.paginacion.skip,
        limit=body.paginacion.limit,
        eleccion_id=body.eleccion_id,
        territorio_id=body.territorio_id,
        partido_id=body.partido_id,
        year=body.year,
        tipo_eleccion=body.tipo_eleccion,
        tipo_territorio=body.tipo_territorio,
        codigo_ccaa=body.codigo_ccaa,
        codigo_provincia=body.codigo_provincia,
        codigo_municipio=body.codigo_municipio,
    )

