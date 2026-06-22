from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import crud
from app.api import routes_elecciones, routes_resultados
from app.database import Base
from app.main import app
from app.models.models import (
    Eleccion,
    Partido,
    ResumenTerritorial,
    Territorio,
    TipoEleccion,
    VotoTerritorial,
)
from app.schemas.resultados import (
    ResultadoCombinadoSearch,
    TotalTerritorioSearch,
    VotoPartidoSearch,
)
from app.schemas.territorios import TerritorioDetail, TerritorioList


@pytest.fixture()
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()

    session.add(TipoEleccion(codigo="G", descripcion="Generales"))
    session.add(
        Eleccion(
            id=1,
            tipo_eleccion="G",
            year="2023",
            mes="07",
            dia="23",
        )
    )
    session.add_all(
        [
            Territorio(
                id=1,
                tipo="circunscripcion",
                codigo_circunscripcion="001",
                nombre="Circunscripción 1",
            ),
            Territorio(
                id=2,
                tipo="circunscripcion",
                codigo_circunscripcion="002",
                nombre="Circunscripción 2",
            ),
            Territorio(
                id=3,
                tipo="ccaa",
                codigo_ccaa="01",
                codigo_provincia="99",
                codigo_circunscripcion="99",
                nombre="Andalucía",
            ),
            Territorio(
                id=4,
                tipo="provincia",
                codigo_ccaa="01",
                codigo_provincia="04",
                codigo_circunscripcion="99",
                nombre="Almería",
                parent_id=3,
            ),
        ]
    )
    session.add(Partido(id=1, siglas="TEST", denominacion="Partido de prueba"))
    session.add_all(
        [
            ResumenTerritorial(id=1, eleccion_id=1, territorio_id=1),
            ResumenTerritorial(id=2, eleccion_id=1, territorio_id=2),
            ResumenTerritorial(id=3, eleccion_id=1, territorio_id=3),
            ResumenTerritorial(id=4, eleccion_id=1, territorio_id=4),
            VotoTerritorial(
                id=1, eleccion_id=1, territorio_id=1, partido_id=1, votos=100
            ),
            VotoTerritorial(
                id=2, eleccion_id=1, territorio_id=2, partido_id=1, votos=200
            ),
            VotoTerritorial(
                id=3, eleccion_id=1, territorio_id=3, partido_id=1, votos=300
            ),
            VotoTerritorial(
                id=4, eleccion_id=1, territorio_id=4, partido_id=1, votos=400
            ),
        ]
    )
    session.commit()

    yield session

    session.close()
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.mark.parametrize(
    "getter",
    [
        crud.get_totales_territorio,
        crud.get_votos_partido,
        crud.get_resultados_combinados,
    ],
)
def test_resultados_filter_by_codigo_circunscripcion(db, getter):
    result = getter(db, codigo_circunscripcion=["001"])

    assert result["total"] == 1
    assert [item.territorio_id for item in result["data"]] == [1]


@pytest.mark.parametrize(
    "getter",
    [
        crud.get_totales_territorio,
        crud.get_votos_partido,
        crud.get_resultados_combinados,
    ],
)
def test_resultados_filter_by_codigo_circunscripcion_99(db, getter):
    result = getter(db, codigo_circunscripcion=["99"])

    assert result["total"] == 2
    assert [item.territorio_id for item in result["data"]] == [3, 4]


def test_territorios_filter_by_codigo_circunscripcion_99(db):
    result = crud.get_territorios(db, codigo_circunscripcion=["99"])

    assert result["total"] == 2
    assert [(item.tipo, item.id) for item in result["data"]] == [
        ("ccaa", 3),
        ("provincia", 4),
    ]


@pytest.mark.parametrize("schema", [TerritorioList, TerritorioDetail])
@pytest.mark.parametrize("territorio_id", [3, 4])
def test_territorio_schemas_return_persisted_codigo_circunscripcion(
    db, schema, territorio_id
):
    territorio = crud.get_territorio(db, territorio_id)

    assert schema.model_validate(territorio).codigo_circunscripcion == "99"


def test_totales_territorio_eleccion_filter_by_codigo_circunscripcion_99(db):
    result = crud.get_totales_territorio_eleccion(
        db,
        eleccion_id=1,
        codigo_circunscripcion=["99"],
    )

    assert result["total"] == 2
    assert [item.territorio_id for item in result["data"]] == [3, 4]


@pytest.mark.parametrize(
    "search_schema",
    [TotalTerritorioSearch, VotoPartidoSearch, ResultadoCombinadoSearch],
)
def test_post_search_schemas_accept_codigo_circunscripcion(search_schema):
    body = search_schema(codigo_circunscripcion=["99", "001"])

    assert body.codigo_circunscripcion == ["99", "001"]


@pytest.mark.parametrize(
    "path",
    [
        "/v1/resultados/totales-territorio",
        "/v1/resultados/votos-partido",
        "/v1/resultados/combinados",
    ],
)
def test_get_openapi_exposes_codigo_circunscripcion(path):
    parameters = app.openapi()["paths"][path]["get"]["parameters"]

    assert "codigo_circunscripcion" in {parameter["name"] for parameter in parameters}


def test_openapi_territorio_list_exposes_codigo_circunscripcion_99_contract():
    schema = app.openapi()["components"]["schemas"]["TerritorioList"]
    field = schema["properties"]["codigo_circunscripcion"]

    assert '"99"' in field["description"]


def test_all_get_endpoints_with_codigo_provincia_also_expose_circunscripcion():
    for path, operations in app.openapi()["paths"].items():
        get_operation = operations.get("get")
        if not get_operation:
            continue

        parameter_names = {
            parameter["name"] for parameter in get_operation.get("parameters", [])
        }
        if "codigo_provincia" in parameter_names:
            assert "codigo_circunscripcion" in parameter_names, path


@pytest.mark.parametrize(
    ("endpoint", "crud_name"),
    [
        (routes_resultados.list_totales_territorio, "get_totales_territorio"),
        (routes_resultados.list_votos_partido, "get_votos_partido"),
        (routes_resultados.list_resultados_combinados, "get_resultados_combinados"),
    ],
)
def test_get_routes_forward_codigo_circunscripcion(monkeypatch, endpoint, crud_name):
    crud_mock = MagicMock()
    monkeypatch.setattr(routes_resultados.crud, crud_name, crud_mock)

    endpoint(
        pagination=SimpleNamespace(skip=0, limit=50),
        codigo_circunscripcion=["001"],
        db=MagicMock(),
        developer=MagicMock(),
    )

    assert crud_mock.call_args.kwargs["codigo_circunscripcion"] == ["001"]


@pytest.mark.parametrize(
    ("endpoint", "crud_name", "search_schema"),
    [
        (
            routes_resultados.search_totales_territorio,
            "get_totales_territorio",
            TotalTerritorioSearch,
        ),
        (
            routes_resultados.search_votos_partido,
            "get_votos_partido",
            VotoPartidoSearch,
        ),
        (
            routes_resultados.search_resultados_combinados,
            "get_resultados_combinados",
            ResultadoCombinadoSearch,
        ),
    ],
)
def test_post_routes_forward_codigo_circunscripcion(
    monkeypatch, endpoint, crud_name, search_schema
):
    crud_mock = MagicMock()
    monkeypatch.setattr(routes_resultados.crud, crud_name, crud_mock)

    endpoint(
        body=search_schema(codigo_circunscripcion=["001"]),
        db=MagicMock(),
        developer=MagicMock(),
    )

    assert crud_mock.call_args.kwargs["codigo_circunscripcion"] == ["001"]


def test_totales_territorio_eleccion_route_forwards_codigo_circunscripcion(
    monkeypatch,
):
    crud_mock = MagicMock()
    monkeypatch.setattr(
        routes_elecciones.crud,
        "get_totales_territorio_eleccion",
        crud_mock,
    )

    routes_elecciones.get_totales_territorio_eleccion(
        eleccion_id=1,
        pagination=SimpleNamespace(skip=0, limit=50),
        codigo_circunscripcion=["002"],
        db=MagicMock(),
        developer=MagicMock(),
    )

    assert crud_mock.call_args.kwargs["codigo_circunscripcion"] == ["002"]
