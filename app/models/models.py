"""
Modelos SQLAlchemy mapeados a las tablas existentes de la base de datos.

IMPORTANTE: La BD se gestiona por separado (db_schema.sql).
Estos modelos NO crean tablas — solo mapean las que ya existen.
"""

import sqlalchemy as sa
from sqlalchemy.orm import relationship

from app.database import Base


# ─────────────────────────────────────────────────────────
# ENUM territorio_tipo (ya existe en la BD, no lo creamos)
# ─────────────────────────────────────────────────────────

territorio_tipo_enum = sa.Enum(
    "ccaa",
    "provincia",
    "municipio",
    "distrito",
    "seccion",
    "circunscripcion",
    "cera",
    name="territorio_tipo",
    create_type=False,  # el tipo ya existe en PostgreSQL
)


# ─────────────────────────────────────────────────────────
# 1. tipos_eleccion
# ─────────────────────────────────────────────────────────

class TipoEleccion(Base):
    __tablename__ = "tipos_eleccion"

    codigo = sa.Column(sa.String(1), primary_key=True)
    descripcion = sa.Column(sa.String(100), nullable=False)

    elecciones = relationship("Eleccion", back_populates="tipo")


# ─────────────────────────────────────────────────────────
# 2. elecciones
# ─────────────────────────────────────────────────────────

class Eleccion(Base):
    __tablename__ = "elecciones"

    id = sa.Column(sa.Integer, primary_key=True)
    tipo_eleccion = sa.Column(sa.String(1), sa.ForeignKey("tipos_eleccion.codigo"), nullable=False)
    year = sa.Column(sa.CHAR(4), nullable=False)
    mes = sa.Column(sa.CHAR(2), nullable=False)
    dia = sa.Column(sa.CHAR(2), nullable=False)
    fecha = sa.Column(sa.Date, nullable=True)
    codigo_ccaa = sa.Column(sa.CHAR(2), nullable=True)
    numero_vuelta = sa.Column(sa.SmallInteger, default=1)
    descripcion = sa.Column(sa.String(255), nullable=True)
    ambito = sa.Column(sa.String(50), nullable=True)
    slug = sa.Column(sa.String(50), nullable=True)

    tipo = relationship("TipoEleccion", back_populates="elecciones")
    resumenes = relationship("ResumenTerritorial", back_populates="eleccion")
    votos = relationship("VotoTerritorial", back_populates="eleccion")



# ─────────────────────────────────────────────────────────
# 3. territorios
# ─────────────────────────────────────────────────────────

class Territorio(Base):
    __tablename__ = "territorios"

    id = sa.Column(sa.Integer, primary_key=True)
    tipo = sa.Column(territorio_tipo_enum, nullable=False)
    codigo_ccaa = sa.Column(sa.CHAR(2), nullable=True)
    codigo_provincia = sa.Column(sa.CHAR(2), nullable=True)
    codigo_municipio = sa.Column(sa.CHAR(3), nullable=True)
    codigo_distrito = sa.Column(sa.CHAR(2), nullable=True)
    codigo_seccion = sa.Column(sa.CHAR(4), nullable=True)
    codigo_circunscripcion = sa.Column(sa.CHAR(3), nullable=True)
    nombre = sa.Column(sa.String(255), nullable=True)
    codigo_completo = sa.Column(sa.String(13), nullable=True)
    parent_id = sa.Column(sa.Integer, sa.ForeignKey("territorios.id"), nullable=True)

    parent = relationship("Territorio", remote_side=[id], back_populates="hijos")
    hijos = relationship("Territorio", back_populates="parent")


# ─────────────────────────────────────────────────────────
# 4. partidos_recode
# ─────────────────────────────────────────────────────────

class PartidoRecode(Base):
    __tablename__ = "partidos_recode"

    id = sa.Column(sa.Integer, primary_key=True)
    partido_recode = sa.Column(sa.String(50), nullable=False, unique=True)
    agrupacion = sa.Column(sa.String(50), nullable=True)
    color = sa.Column(sa.String(7), nullable=True)

    partidos = relationship("Partido", back_populates="recode")


# ─────────────────────────────────────────────────────────
# 5. partidos
# ─────────────────────────────────────────────────────────

class Partido(Base):
    __tablename__ = "partidos"

    id = sa.Column(sa.Integer, primary_key=True)
    partido_recode_id = sa.Column(sa.Integer, sa.ForeignKey("partidos_recode.id"), nullable=True)
    siglas = sa.Column(sa.String(255), nullable=True)
    denominacion = sa.Column(sa.String(255), nullable=True)

    recode = relationship("PartidoRecode", back_populates="partidos")


# ─────────────────────────────────────────────────────────
# 6. resumen_territorial
# ─────────────────────────────────────────────────────────

class ResumenTerritorial(Base):
    __tablename__ = "resumen_territorial"

    id = sa.Column(sa.Integer, primary_key=True)
    eleccion_id = sa.Column(sa.Integer, sa.ForeignKey("elecciones.id"), nullable=False)
    territorio_id = sa.Column(sa.Integer, sa.ForeignKey("territorios.id"), nullable=False)
    censo_ine = sa.Column(sa.Integer, nullable=True)
    participacion_1 = sa.Column(sa.Integer, nullable=True)
    participacion_2 = sa.Column(sa.Integer, nullable=True)
    participacion_3 = sa.Column(sa.Integer, nullable=True)
    votos_validos = sa.Column(sa.Integer, nullable=True)
    abstenciones = sa.Column(sa.Integer, nullable=True)
    votos_blancos = sa.Column(sa.Integer, nullable=True)
    votos_nulos = sa.Column(sa.Integer, nullable=True)
    nrepresentantes = sa.Column(sa.Integer, nullable=True)

    eleccion = relationship("Eleccion", back_populates="resumenes")
    territorio = relationship("Territorio")


# ─────────────────────────────────────────────────────────
# 7. votos_territoriales
# ─────────────────────────────────────────────────────────

class VotoTerritorial(Base):
    __tablename__ = "votos_territoriales"

    id = sa.Column(sa.Integer, primary_key=True)
    eleccion_id = sa.Column(sa.Integer, sa.ForeignKey("elecciones.id"), nullable=False)
    territorio_id = sa.Column(sa.Integer, sa.ForeignKey("territorios.id"), nullable=False)
    partido_id = sa.Column(sa.Integer, sa.ForeignKey("partidos.id"), nullable=False)
    votos = sa.Column(sa.Integer, nullable=True)
    representantes = sa.Column(sa.Integer, nullable=True)

    eleccion = relationship("Eleccion", back_populates="votos")
    territorio = relationship("Territorio")
    partido = relationship("Partido")

