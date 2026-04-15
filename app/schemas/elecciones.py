from __future__ import annotations

import datetime
from pydantic import BaseModel, ConfigDict


# ─── Tipos de elección ──────────────────────────────────

class TipoEleccionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    codigo: str
    descripcion: str


# ─── Elecciones ─────────────────────────────────────────

class EleccionList(BaseModel):
    """Representación resumida para listados."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo_eleccion: str
    year: str
    mes: str
    dia: str
    fecha: datetime.date | None = None
    descripcion: str | None = None
    ambito: str | None = None
    slug: str | None = None


class EleccionDetail(BaseModel):
    """Representación completa con tipo expandido."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo_eleccion: str
    year: str
    mes: str
    dia: str
    fecha: datetime.date | None = None
    codigo_ccaa: str | None = None
    numero_vuelta: int | None = None
    descripcion: str | None = None
    ambito: str | None = None
    slug: str | None = None
    tipo: TipoEleccionSchema | None = None


# ─── Fuentes de elecciones ──────────────────────────────

class EleccionFuenteSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    eleccion_id: int
    fuente: str
    url_fuente: str
    observaciones: str | None = None
