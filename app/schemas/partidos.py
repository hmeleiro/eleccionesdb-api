from __future__ import annotations

from pydantic import BaseModel, ConfigDict


# ─── Partidos recode (agrupaciones) ─────────────────────

class PartidoRecodeSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    partido_recode: str
    agrupacion: str | None = None
    color: str | None = None


class PartidoRecodeDetail(PartidoRecodeSchema):
    """Detalle de un recode con la lista de partidos asociados."""
    partidos: list[PartidoList] = []


# ─── Partidos ───────────────────────────────────────────

class PartidoList(BaseModel):
    """Representación resumida para listados."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    siglas: str | None = None
    denominacion: str | None = None
    partido_recode_id: int | None = None


class PartidoDetail(BaseModel):
    """Representación completa con recode expandido."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    siglas: str | None = None
    denominacion: str | None = None
    partido_recode_id: int | None = None
    recode: PartidoRecodeSchema | None = None


# Resolver referencia circular (PartidoRecodeDetail → PartidoList)
PartidoRecodeDetail.model_rebuild()
