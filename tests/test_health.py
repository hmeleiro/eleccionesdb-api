"""
Tests básicos para el endpoint /health.

Usa TestClient de FastAPI (basado en httpx).
No requiere conexión real a la BD: se mockea la dependency get_db.
"""

from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.main import app
from app.database import get_db


def _override_get_db():
    """Proporciona un mock de sesión para tests sin BD real."""
    db = MagicMock()
    db.execute.return_value = None  # simula SELECT 1 exitoso
    try:
        yield db
    finally:
        pass


app.dependency_overrides[get_db] = _override_get_db
client = TestClient(app)


def test_health_returns_200():
    response = client.get("/health")
    assert response.status_code == 200


def test_health_response_structure():
    response = client.get("/health")
    data = response.json()
    assert "status" in data
    assert "environment" in data
    assert "database" in data
    assert data["status"] == "ok"


def test_health_database_ok():
    """Cuando la BD responde, database debe ser 'ok'."""
    response = client.get("/health")
    data = response.json()
    assert data["database"] == "ok"


def test_openapi_docs_available():
    """Verificar que la documentación OpenAPI está accesible."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "Elecciones DB API"
    # Debe tener al menos los paths de health y elecciones
    assert "/health" in schema["paths"]
    assert "/v1/elecciones" in schema["paths"]
