from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.partidos import PartidoList, PartidoRecodeSchema
from app.schemas.territorios import TerritorioList
from app.schemas.elecciones import EleccionList


# ─── Totales territorio ─────────────────────────────────

class TotalTerritorioSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    eleccion_id: int
    territorio_id: int
    censo_ine: int | None = None
    participacion_1: int | None = None
    participacion_2: int | None = None
    participacion_3: int | None = None
    votos_validos: int | None = None
    abstenciones: int | None = None
    votos_blancos: int | None = None
    votos_nulos: int | None = None
    nrepresentantes: int | None = None


# ─── Votos partido ──────────────────────────────────────

class VotoPartidoSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    eleccion_id: int
    territorio_id: int
    partido_id: int
    votos: int | None = None
    representantes: int | None = None


class VotoPartidoDetalleSchema(BaseModel):
    """Voto con datos del partido expandidos (para desglose de resultados)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    eleccion_id: int
    territorio_id: int
    partido_id: int
    votos: int | None = None
    representantes: int | None = None
    partido: PartidoList


# ─── Resultado completo de una elección en un territorio ─

class ResultadoCompletoSchema(BaseModel):
    """Totales territorio + desglose de votos por partido para un territorio concreto."""
    totales_territorio: TotalTerritorioSchema | None = None
    votos_partido: list[VotoPartidoDetalleSchema] = []


# ─── Resultado combinado (votos + resumen + partido recode) ─

class PartidoConRecodeSchema(BaseModel):
    """Partido con su recode/agrupación expandida inline."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    siglas: str | None = None
    denominacion: str | None = None
    partido_recode_id: int | None = None
    recode: PartidoRecodeSchema | None = None


class ResultadoCombinadoSchema(BaseModel):
    """Voto territorial con partido+recode, territorio y elección expandidos."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    eleccion_id: int
    territorio_id: int
    partido_id: int
    votos: int | None = None
    representantes: int | None = None
    partido: PartidoConRecodeSchema
    territorio: TerritorioList
    eleccion: EleccionList


# ─── Schemas para filtros complejos vía POST ────────────

class SearchPagination(BaseModel):
    """Paginación para endpoints POST de búsqueda compleja."""
    skip: int = Field(default=0, ge=0, description="Número de registros a saltar")
    limit: int = Field(default=50, ge=1, le=500, description="Número máximo de registros a devolver")


class BaseResultadosSearch(BaseModel):
    """Filtros comunes compartidos por los tres endpoints POST de resultados."""
    paginacion: SearchPagination = Field(
        default_factory=SearchPagination,
        description="Parámetros de paginación (skip, limit)",
    )
    eleccion_id: Optional[list[int]] = Field(
        default=None, description="Filtrar por ID(s) de elección"
    )
    territorio_id: Optional[list[int]] = Field(
        default=None, description="Filtrar por ID(s) de territorio"
    )
    year: Optional[list[str]] = Field(
        default=None, description="Filtrar por año(s) electoral(es), p.ej. ['2019', '2023']"
    )
    tipo_eleccion: Optional[list[str]] = Field(
        default=None, description="Filtrar por tipo(s) de elección, p.ej. ['G', 'A', 'M', 'E']"
    )
    tipo_territorio: Optional[list[str]] = Field(
        default=None,
        description="Filtrar por tipo(s) de territorio, p.ej. ['municipio', 'provincia', 'ccaa']",
    )
    codigo_ccaa: Optional[list[str]] = Field(
        default=None, description="Filtrar por código(s) de comunidad autónoma, p.ej. ['01', '13']"
    )
    codigo_provincia: Optional[list[str]] = Field(
        default=None, description="Filtrar por código(s) de provincia, p.ej. ['28', '08']"
    )
    codigo_municipio: Optional[list[str]] = Field(
        default=None,
        description="Filtrar por código(s) de municipio INE, p.ej. ['28001', '28002']. "
                    "Usa este endpoint POST cuando la lista sea larga para evitar errores 414.",
    )


class TotalTerritorioSearch(BaseResultadosSearch):
    """Filtros para POST /v1/resultados/totales-territorio."""


class VotoPartidoSearch(BaseResultadosSearch):
    """Filtros para POST /v1/resultados/votos-partido."""
    partido_id: Optional[list[int]] = Field(
        default=None, description="Filtrar por ID(s) de partido"
    )


class ResultadoCombinadoSearch(BaseResultadosSearch):
    """Filtros para POST /v1/resultados/combinados."""
    partido_id: Optional[list[int]] = Field(
        default=None, description="Filtrar por ID(s) de partido"
    )

