"""
Funciones de acceso a datos (CRUD — solo lectura por ahora).

Cada función recibe una sesión de SQLAlchemy y parámetros de filtro/paginación opcionales.
Devuelve objetos del ORM que las rutas serializan via Pydantic.
"""

from typing import Optional

from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.models import (
    TipoEleccion,
    Eleccion,
    Territorio,
    PartidoRecode,
    Partido,
    ResumenTerritorial,
    VotoTerritorial,
)


# ─────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────

def _paginate(query, skip: int, limit: int) -> dict:
    """Aplica paginación y devuelve total + datos."""
    total = query.order_by(None).count()
    data = query.offset(skip).limit(limit).all()
    return {"total": total, "skip": skip, "limit": limit, "data": data}


def _apply_in_filter(query, column, values):
    """Aplica filtro .in_() si values es una lista no vacía."""
    if values:
        query = query.filter(column.in_(values))
    return query


def _apply_eleccion_filters(query, model, year=None, tipo_eleccion=None, eleccion_id=None):
    """Join con Eleccion si hay filtros de año o tipo_eleccion."""
    query = _apply_in_filter(query, model.eleccion_id, eleccion_id)
    if year or tipo_eleccion:
        query = query.join(Eleccion, model.eleccion_id == Eleccion.id)
        query = _apply_in_filter(query, Eleccion.year, year)
        query = _apply_in_filter(query, Eleccion.tipo_eleccion, tipo_eleccion)
    return query


def _apply_territorio_filters(query, model,
                               territorio_id=None, tipo_territorio=None,
                               codigo_ccaa=None, codigo_provincia=None,
                               codigo_municipio=None):
    """Join con Territorio si hay filtros territoriales."""
    query = _apply_in_filter(query, model.territorio_id, territorio_id)
    if tipo_territorio or codigo_ccaa or codigo_provincia or codigo_municipio:
        query = query.join(Territorio, model.territorio_id == Territorio.id)
        query = _apply_in_filter(query, Territorio.tipo, tipo_territorio)
        query = _apply_in_filter(query, Territorio.codigo_ccaa, codigo_ccaa)
        query = _apply_in_filter(query, Territorio.codigo_provincia, codigo_provincia)
        query = _apply_in_filter(query, Territorio.codigo_municipio, codigo_municipio)
    return query


# ─────────────────────────────────────────────────────────
# Tipos de elección
# ─────────────────────────────────────────────────────────

def get_tipos_eleccion(db: Session) -> list[TipoEleccion]:
    return db.query(TipoEleccion).order_by(TipoEleccion.codigo).all()


def get_tipo_eleccion(db: Session, codigo: str) -> Optional[TipoEleccion]:
    return db.query(TipoEleccion).filter(TipoEleccion.codigo == codigo).first()


# ─────────────────────────────────────────────────────────
# Elecciones
# ─────────────────────────────────────────────────────────

def get_elecciones(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    tipo_eleccion: Optional[list[str]] = None,
    year: Optional[list[str]] = None,
    ambito: Optional[list[str]] = None,
) -> dict:
    query = db.query(Eleccion)
    query = _apply_in_filter(query, Eleccion.tipo_eleccion, tipo_eleccion)
    query = _apply_in_filter(query, Eleccion.year, year)
    query = _apply_in_filter(query, Eleccion.ambito, ambito)
    return _paginate(query.order_by(Eleccion.id), skip, limit)


def get_eleccion(db: Session, eleccion_id: int) -> Optional[Eleccion]:
    return (
        db.query(Eleccion)
        .options(joinedload(Eleccion.tipo))
        .filter(Eleccion.id == eleccion_id)
        .first()
    )


# ─────────────────────────────────────────────────────────
# Territorios
# ─────────────────────────────────────────────────────────

def get_territorios(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    tipo: Optional[list[str]] = None,
    codigo_ccaa: Optional[list[str]] = None,
    codigo_provincia: Optional[list[str]] = None,
    codigo_municipio: Optional[list[str]] = None,
    codigo_circunscripcion: Optional[list[str]] = None,
    nombre: Optional[str] = None,
) -> dict:
    query = db.query(Territorio)
    query = _apply_in_filter(query, Territorio.tipo, tipo)
    query = _apply_in_filter(query, Territorio.codigo_ccaa, codigo_ccaa)
    query = _apply_in_filter(query, Territorio.codigo_provincia, codigo_provincia)
    query = _apply_in_filter(query, Territorio.codigo_municipio, codigo_municipio)
    query = _apply_in_filter(query, Territorio.codigo_circunscripcion, codigo_circunscripcion)
    if nombre:
        query = query.filter(Territorio.nombre.ilike(f"%{nombre}%"))
    return _paginate(query.order_by(Territorio.id), skip, limit)


def get_territorio(db: Session, territorio_id: int) -> Optional[Territorio]:
    return db.query(Territorio).filter(Territorio.id == territorio_id).first()


def get_hijos_territorio(
    db: Session,
    territorio_id: int,
    skip: int = 0,
    limit: int = 50,
) -> dict:
    query = (
        db.query(Territorio)
        .filter(Territorio.parent_id == territorio_id)
        .order_by(Territorio.id)
    )
    return _paginate(query, skip, limit)


# ─────────────────────────────────────────────────────────
# Partidos
# ─────────────────────────────────────────────────────────

def get_partidos(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    siglas: Optional[str] = None,
) -> dict:
    query = db.query(Partido)
    if siglas:
        query = query.filter(Partido.siglas.ilike(f"%{siglas}%"))
    return _paginate(query.order_by(Partido.id), skip, limit)


def get_partido(db: Session, partido_id: int) -> Optional[Partido]:
    return (
        db.query(Partido)
        .options(joinedload(Partido.recode))
        .filter(Partido.id == partido_id)
        .first()
    )


def get_partidos_recode(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    agrupacion: Optional[str] = None,
) -> dict:
    query = db.query(PartidoRecode)
    if agrupacion:
        query = query.filter(PartidoRecode.agrupacion.ilike(f"%{agrupacion}%"))
    return _paginate(query.order_by(PartidoRecode.id), skip, limit)


def get_partido_recode(db: Session, partido_recode_id: int) -> Optional[PartidoRecode]:
    return (
        db.query(PartidoRecode)
        .options(joinedload(PartidoRecode.partidos))
        .filter(PartidoRecode.id == partido_recode_id)
        .first()
    )


# ─────────────────────────────────────────────────────────
# Resultados — totales territorio
# ─────────────────────────────────────────────────────────

def get_totales_territorio(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    eleccion_id: Optional[list[int]] = None,
    territorio_id: Optional[list[int]] = None,
    year: Optional[list[str]] = None,
    tipo_eleccion: Optional[list[str]] = None,
    tipo_territorio: Optional[list[str]] = None,
    codigo_ccaa: Optional[list[str]] = None,
    codigo_provincia: Optional[list[str]] = None,
    codigo_municipio: Optional[list[str]] = None,
) -> dict:
    query = db.query(ResumenTerritorial)
    query = _apply_eleccion_filters(query, ResumenTerritorial, year, tipo_eleccion, eleccion_id)
    query = _apply_territorio_filters(query, ResumenTerritorial, territorio_id, tipo_territorio, codigo_ccaa, codigo_provincia, codigo_municipio)
    return _paginate(query.order_by(ResumenTerritorial.id), skip, limit)


def get_votos_partido(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    eleccion_id: Optional[list[int]] = None,
    territorio_id: Optional[list[int]] = None,
    partido_id: Optional[list[int]] = None,
    year: Optional[list[str]] = None,
    tipo_eleccion: Optional[list[str]] = None,
    tipo_territorio: Optional[list[str]] = None,
    codigo_ccaa: Optional[list[str]] = None,
    codigo_provincia: Optional[list[str]] = None,
    codigo_municipio: Optional[list[str]] = None,
) -> dict:
    query = db.query(VotoTerritorial)
    query = _apply_eleccion_filters(query, VotoTerritorial, year, tipo_eleccion, eleccion_id)
    query = _apply_territorio_filters(query, VotoTerritorial, territorio_id, tipo_territorio, codigo_ccaa, codigo_provincia, codigo_municipio)
    query = _apply_in_filter(query, VotoTerritorial.partido_id, partido_id)
    return _paginate(query.order_by(VotoTerritorial.id), skip, limit)


# ─── Totales territorio para una elección ──────────────────

def get_totales_territorio_eleccion(
    db: Session,
    eleccion_id: int,
    skip: int = 0,
    limit: int = 50,
    territorio_id: Optional[list[int]] = None,
    tipo_territorio: Optional[list[str]] = None,
    codigo_ccaa: Optional[list[str]] = None,
    codigo_provincia: Optional[list[str]] = None,
    codigo_municipio: Optional[list[str]] = None,
) -> dict:
    query = (
        db.query(ResumenTerritorial)
        .filter(ResumenTerritorial.eleccion_id == eleccion_id)
    )
    query = _apply_territorio_filters(query, ResumenTerritorial, territorio_id, tipo_territorio, codigo_ccaa, codigo_provincia, codigo_municipio)
    return _paginate(query.order_by(ResumenTerritorial.id), skip, limit)


def get_resultado_completo(
    db: Session,
    eleccion_id: int,
    territorio_id: int,
) -> dict:
    """Totales territorio + votos desglosados por partido para una elección y territorio concretos."""
    resumen = (
        db.query(ResumenTerritorial)
        .filter(
            ResumenTerritorial.eleccion_id == eleccion_id,
            ResumenTerritorial.territorio_id == territorio_id,
        )
        .first()
    )
    votos = (
        db.query(VotoTerritorial)
        .options(joinedload(VotoTerritorial.partido))
        .filter(
            VotoTerritorial.eleccion_id == eleccion_id,
            VotoTerritorial.territorio_id == territorio_id,
        )
        .order_by(VotoTerritorial.votos.desc().nulls_last())
        .all()
    )
    return {"totales_territorio": resumen, "votos_partido": votos}


# ─── Combinados: votos + partido recode + territorio + elección ─

def get_resultados_combinados(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    eleccion_id: Optional[list[int]] = None,
    territorio_id: Optional[list[int]] = None,
    partido_id: Optional[list[int]] = None,
    year: Optional[list[str]] = None,
    tipo_eleccion: Optional[list[str]] = None,
    tipo_territorio: Optional[list[str]] = None,
    codigo_ccaa: Optional[list[str]] = None,
    codigo_provincia: Optional[list[str]] = None,
    codigo_municipio: Optional[list[str]] = None,
) -> dict:
    query = (
        db.query(VotoTerritorial)
        .options(
            joinedload(VotoTerritorial.partido).joinedload(Partido.recode),
            selectinload(VotoTerritorial.territorio),
            selectinload(VotoTerritorial.eleccion),
        )
    )
    query = _apply_eleccion_filters(query, VotoTerritorial, year, tipo_eleccion, eleccion_id)
    query = _apply_territorio_filters(query, VotoTerritorial, territorio_id, tipo_territorio, codigo_ccaa, codigo_provincia, codigo_municipio)
    query = _apply_in_filter(query, VotoTerritorial.partido_id, partido_id)
    return _paginate(query.order_by(VotoTerritorial.id), skip, limit)

