"""Comprobaciones de construcción de la API sin credenciales."""

from __future__ import annotations

from fastapi.testclient import TestClient

from inflacion_lab.api.app import create_app


def test_api_import_and_liveness_do_not_require_database_configuration(monkeypatch) -> None:
    monkeypatch.delenv("DATABASE_URL_API", raising=False)
    client = TestClient(create_app())

    response = client.get("/api/inflacion/v1/health/live")

    assert response.status_code == 200
    assert response.json() == {"estado": "activo"}

    ready = client.get("/api/inflacion/v1/health/ready")

    assert ready.status_code == 503
    assert ready.json()["codigo"] == "base_no_disponible"


def test_openapi_documents_the_versioned_prefix() -> None:
    schema = create_app().openapi()

    assert "/api/inflacion/v1/catalogo" in schema["paths"]
    assert "/api/inflacion/v1/health/ready" in schema["paths"]
