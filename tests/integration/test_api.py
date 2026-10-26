"""Contratos HTTP de lectura sobre PostgreSQL real y aislado."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, insert, select

from inflacion_lab.api.app import create_app
from inflacion_lab.catalogo import load_catalog
from inflacion_lab.db.catalogo import register_catalog
from inflacion_lab.db.tablas import archivos_fuente, ejecuciones_etl, observaciones, series

pytestmark = pytest.mark.integration


def _general_series_id(connection) -> int:
    value = connection.scalar(
        select(series.c.id).where(series.c.geografia_id == "mx", series.c.rubro_id == "general")
    )
    assert value is not None
    return value


def _seed_api_data(connection) -> None:
    register_catalog(connection, load_catalog())
    serie_id = _general_series_id(connection)
    periods = [date(2020, 1, 1), date(2020, 2, 1), date(2021, 1, 1), date(2021, 2, 1)]
    connection.execute(
        delete(observaciones).where(
            observaciones.c.serie_id == serie_id,
            observaciones.c.periodo.in_(periods),
        )
    )
    execution_id = uuid4()
    completed = datetime(2026, 10, 26, 18, 0, tzinfo=UTC)
    connection.execute(
        insert(ejecuciones_etl).values(
            id=execution_id,
            modo="bootstrap",
            iniciada_en=completed,
            finalizada_en=completed,
            estado="exitosa",
            version_catalogo="api-test",
        )
    )
    file_id = connection.scalar(
        insert(archivos_fuente)
        .values(
            ejecucion_id=execution_id,
            geografia_id="mx",
            sha256="d" * 64,
            ruta_relativa="raw/api-test.csv",
        )
        .returning(archivos_fuente.c.id)
    )
    assert file_id is not None
    connection.execute(
        insert(observaciones),
        [
            {
                "serie_id": serie_id,
                "periodo": period,
                "valor": value,
                "archivo_fuente_id": file_id,
                "ejecucion_id": execution_id,
            }
            for period, value in {
                date(2020, 1, 1): Decimal("100"),
                date(2020, 2, 1): Decimal("110"),
                date(2021, 1, 1): Decimal("120"),
                date(2021, 2, 1): Decimal("121"),
            }.items()
        ],
    )


def test_catalog_summary_and_history_follow_the_metrics_contract(migrated_engine) -> None:
    with migrated_engine.begin() as connection:
        _seed_api_data(connection)
    client = TestClient(create_app(engine=migrated_engine))

    catalog = client.get("/api/inflacion/v1/catalogo")
    summary = client.get("/api/inflacion/v1/resumen?geografia=mx&periodo=2021-01")
    history = client.get(
        "/api/inflacion/v1/series?geografia=mx&rubro=general&medida=anual&desde=2021-01&hasta=2021-02"
    )

    assert catalog.status_code == 200
    assert len(catalog.json()["datos"]["geografias"]) == 88
    assert catalog.json()["meta"]["estado"] == "disponible"
    assert summary.json()["meta"]["periodo_fuente_max"].count("-") == 1
    assert summary.json()["datos"]["indice"]["valor"] == 120.0
    assert summary.json()["datos"]["anual"] == {
        "valor": 20.0,
        "estado": "disponible",
        "unidad": "porcentaje",
    }
    assert history.json()["datos"] == [
        {"periodo": "2021-01", "valor": 20.0, "estado": "disponible"},
        {"periodo": "2021-02", "valor": 10.0, "estado": "disponible"},
    ]


def test_etag_and_parameter_errors_are_explicit(migrated_engine) -> None:
    with migrated_engine.begin() as connection:
        _seed_api_data(connection)
    client = TestClient(create_app(engine=migrated_engine))
    url = "/api/inflacion/v1/series?geografia=mx&rubro=general&desde=2021-01&hasta=2021-02"

    initial = client.get(url)
    cached = client.get(url, headers={"If-None-Match": initial.headers["etag"]})
    unknown = client.get("/api/inflacion/v1/resumen?geografia=inexistente")
    inverted = client.get(
        "/api/inflacion/v1/series?geografia=mx&rubro=general&desde=2021-02&hasta=2021-01"
    )
    excessive = client.get(
        "/api/inflacion/v1/series?geografia=mx&rubro=general&desde=2000-01&hasta=2021-01"
    )

    assert initial.headers["cache-control"] == "public, max-age=300"
    assert cached.status_code == 304
    assert unknown.json()["codigo"] == "geografia_desconocida"
    assert inverted.json()["codigo"] == "rango_invertido"
    assert excessive.json()["codigo"] == "rango_excesivo"
