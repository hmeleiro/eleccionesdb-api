from __future__ import annotations

from pydantic import BaseModel, ConfigDict

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

