from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


_CODIGO_CIRCUNSCRIPCION_DESCRIPTION = (
    'Código de circunscripción persistido; para CCAA y provincias es "99".'
)


class TerritorioList(BaseModel):
    """Representación resumida para listados."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo: str
    nombre: str | None = None
    codigo_completo: str | None = None
    codigo_ccaa: str | None = None
    codigo_provincia: str | None = None
    codigo_circunscripcion: str | None = Field(
        default=None,
        description=_CODIGO_CIRCUNSCRIPCION_DESCRIPTION,
    )


class TerritorioDetail(BaseModel):
    """Representación completa con todos los códigos."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo: str
    codigo_ccaa: str | None = None
    codigo_provincia: str | None = None
    codigo_municipio: str | None = None
    codigo_distrito: str | None = None
    codigo_seccion: str | None = None
    codigo_circunscripcion: str | None = Field(
        default=None,
        description=_CODIGO_CIRCUNSCRIPCION_DESCRIPTION,
    )
    nombre: str | None = None
    codigo_completo: str | None = None
    parent_id: int | None = None
