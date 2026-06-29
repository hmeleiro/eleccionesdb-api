from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import crud
from app.api import routes_partidos
from app.database import Base
from app.main import app
from app.models.models import PartidoRecode
from app.schemas.partidos import PartidoRecodeSchema


@pytest.fixture()
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()

    session.add_all(
        [
            PartidoRecode(
                id=1,
                partido_recode="PSOE",
                agrupacion="PSOE",
                color="#E30613",
                bloque="izquierda",
                color_pastel="#F8B6BC",
                color_oscuro="#7A0008",
            ),
            PartidoRecode(
                id=2,
                partido_recode="PP",
                agrupacion="AP/PP",
                color="#0056A0",
                bloque="derecha",
                color_pastel="#B8D8F2",
                color_oscuro="#002D55",
            ),
        ]
    )
    session.commit()

    yield session

    session.close()
    Base.metadata.drop_all(engine)
    engine.dispose()


def test_partido_recode_schema_exposes_new_columns(db):
    recode = crud.get_partido_recode(db, 1)
    data = PartidoRecodeSchema.model_validate(recode).model_dump()

    assert data["bloque"] == "izquierda"
    assert data["color_pastel"] == "#F8B6BC"
    assert data["color_oscuro"] == "#7A0008"


def test_partidos_recode_can_filter_by_bloque(db):
    result = crud.get_partidos_recode(db, bloque="dere")

    assert result["total"] == 1
    assert result["data"][0].partido_recode == "PP"


def test_partidos_recode_route_forwards_bloque(monkeypatch):
    crud_mock = MagicMock()
    monkeypatch.setattr(routes_partidos.crud, "get_partidos_recode", crud_mock)

    routes_partidos.list_partidos_recode(
        pagination=SimpleNamespace(skip=0, limit=50),
        agrupacion=None,
        bloque="izquierda",
        db=MagicMock(),
        developer=MagicMock(),
    )

    assert crud_mock.call_args.kwargs["bloque"] == "izquierda"


def test_openapi_exposes_partido_recode_new_columns_and_bloque_filter():
    app.openapi_schema = None
    schema = app.openapi()

    recode_fields = schema["components"]["schemas"]["PartidoRecodeSchema"]["properties"]
    assert {"bloque", "color_pastel", "color_oscuro"} <= set(recode_fields)

    parameters = schema["paths"]["/v1/partidos-recode"]["get"]["parameters"]
    assert "bloque" in {parameter["name"] for parameter in parameters}
