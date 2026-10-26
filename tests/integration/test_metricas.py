"""Pruebas independientes de las fórmulas canónicas de inflación."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import delete, insert, select

from inflacion_lab.catalogo import load_catalog
from inflacion_lab.db.catalogo import register_catalog
from inflacion_lab.db.metricas import diferencia_tasas, razon_indices, serie_metricas
from inflacion_lab.db.tablas import archivos_fuente, ejecuciones_etl, observaciones, series

pytestmark = pytest.mark.integration


def _series_id(connection, geografia_id: str) -> int:
    value = connection.scalar(
        select(series.c.id).where(
            series.c.geografia_id == geografia_id,
            series.c.rubro_id == "general",
        )
    )
    assert value is not None
    return value


def _seed(connection, geografia_id: str, values: dict[date, Decimal | None]) -> int:
    register_catalog(connection, load_catalog())
    serie_id = _series_id(connection, geografia_id)
    periods = list(values)
    connection.execute(
        delete(observaciones).where(
            observaciones.c.serie_id == serie_id,
            observaciones.c.periodo.in_(periods),
        )
    )
    execution_id = uuid4()
    connection.execute(
        insert(ejecuciones_etl).values(
            id=execution_id,
            modo="bootstrap",
            iniciada_en=datetime.now(UTC),
            estado="exitosa",
            version_catalogo="metricas-test",
        )
    )
    file_id = connection.scalar(
        insert(archivos_fuente)
        .values(
            ejecucion_id=execution_id,
            geografia_id=geografia_id,
            sha256="c" * 64,
            ruta_relativa="raw/metricas-test.csv",
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
            for period, value in values.items()
        ],
    )
    return serie_id


def test_rates_join_the_exact_calendar_month_before_filtering(migrated_engine) -> None:
    values = {
        date(2018, 1, 1): Decimal("100"),
        date(2018, 3, 1): Decimal("110"),
        date(2019, 1, 1): Decimal("120"),
        date(2019, 3, 1): Decimal("121"),
        date(2019, 4, 1): Decimal("121"),
        date(2019, 5, 1): None,
        date(2019, 6, 1): Decimal("100"),
        date(2019, 7, 1): Decimal("90"),
    }
    with migrated_engine.begin() as connection:
        serie_id = _seed(connection, "mx", values)
        annual = serie_metricas(
            connection,
            serie_id=serie_id,
            medida="anual",
            desde=date(2019, 1, 1),
            hasta=date(2019, 5, 1),
        )
        monthly = serie_metricas(
            connection,
            serie_id=serie_id,
            medida="mensual",
            desde=date(2019, 1, 1),
            hasta=date(2019, 5, 1),
        )
        first_year = serie_metricas(
            connection,
            serie_id=serie_id,
            medida="anual",
            desde=date(2018, 1, 1),
            hasta=date(2018, 3, 1),
        )
        negative = serie_metricas(
            connection,
            serie_id=serie_id,
            medida="mensual",
            desde=date(2019, 7, 1),
            hasta=date(2019, 7, 1),
        )

    assert [(item.periodo, item.valor, item.estado) for item in annual] == [
        (date(2019, 1, 1), Decimal("20"), "disponible"),
        (date(2019, 3, 1), Decimal("10"), "disponible"),
        (date(2019, 4, 1), None, "sin_denominador"),
        (date(2019, 5, 1), None, "sin_valor_fuente"),
    ]
    assert [(item.periodo, item.valor, item.estado) for item in monthly] == [
        (date(2019, 1, 1), None, "sin_denominador"),
        (date(2019, 3, 1), None, "sin_denominador"),
        (date(2019, 4, 1), Decimal("0"), "disponible"),
        (date(2019, 5, 1), None, "sin_valor_fuente"),
    ]
    assert annual[0].unidad == "porcentaje"
    assert [(item.periodo, item.valor, item.estado) for item in first_year] == [
        (date(2018, 1, 1), None, "sin_denominador"),
        (date(2018, 3, 1), None, "sin_denominador"),
    ]
    assert negative[0].valor == Decimal("-10")
    assert negative[0].estado == "disponible"


def test_ratio_and_rate_difference_keep_decimal_semantics(migrated_engine) -> None:
    mexico = {
        date(2018, 1, 1): Decimal("100"),
        date(2019, 1, 1): Decimal("120"),
    }
    jalisco = {
        date(2018, 1, 1): Decimal("100"),
        date(2019, 1, 1): Decimal("110"),
    }
    with migrated_engine.begin() as connection:
        mexico_id = _seed(connection, "mx", mexico)
        jalisco_id = _seed(connection, "entidad-14", jalisco)
        ratio = razon_indices(
            connection,
            serie_id=mexico_id,
            inicio=date(2018, 1, 1),
            fin=date(2019, 1, 1),
        )
        difference = diferencia_tasas(
            connection,
            primera_serie_id=mexico_id,
            segunda_serie_id=jalisco_id,
            periodo=date(2019, 1, 1),
            medida="anual",
        )

    assert ratio.razon == Decimal("1.2")
    assert ratio.variacion == Decimal("20")
    assert ratio.estado == "disponible"
    assert difference.valor == Decimal("10")
    assert difference.unidad == "puntos_porcentuales"


def test_ratio_reports_a_missing_exact_month(migrated_engine) -> None:
    with migrated_engine.begin() as connection:
        serie_id = _seed(connection, "mx", {date(2020, 1, 1): Decimal("100")})
        connection.execute(
            delete(observaciones).where(
                observaciones.c.serie_id == serie_id,
                observaciones.c.periodo == date(2020, 2, 1),
            )
        )
        result = razon_indices(
            connection,
            serie_id=serie_id,
            inicio=date(2020, 1, 1),
            fin=date(2020, 2, 1),
        )

    assert result.razon is None
    assert result.variacion is None
    assert result.estado == "no_publicado"
