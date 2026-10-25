"""Comprobaciones del contrato en PostgreSQL real."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import pytest
from alembic.config import Config
from sqlalchemy import delete, func, insert, select
from sqlalchemy.exc import IntegrityError

from alembic import command
from inflacion_lab.catalogo import load_catalog
from inflacion_lab.db.catalogo import register_catalog
from inflacion_lab.db.tablas import (
    archivos_fuente,
    ejecuciones_etl,
    geografias,
    observaciones,
    revisiones_observacion,
    rubros,
    series,
)

pytestmark = pytest.mark.integration


def test_migration_is_repeatable(migrated_engine) -> None:
    config = Config("alembic.ini")
    command.upgrade(config, "head")
    with migrated_engine.connect() as connection:
        tables = connection.dialect.get_table_names(connection)
    assert set(tables) >= {
        "geografias",
        "rubros",
        "series",
        "ejecuciones_etl",
        "archivos_fuente",
        "observaciones",
        "revisiones_observacion",
    }


def test_catalog_registration_is_idempotent(migrated_engine) -> None:
    catalog = load_catalog(Path("config/series.yml"))
    with migrated_engine.begin() as connection:
        register_catalog(connection, catalog)
        register_catalog(connection, catalog)
        assert connection.scalar(select(func.count()).select_from(geografias)) == 88
        assert connection.scalar(select(func.count()).select_from(rubros)) == 9
        assert connection.scalar(select(func.count()).select_from(series)) == 792


def test_observations_preserve_decimals_and_nulls_and_enforce_constraints(migrated_engine) -> None:
    catalog = load_catalog(Path("config/series.yml"))
    execution_id = uuid4()
    with migrated_engine.begin() as connection:
        register_catalog(connection, catalog)
        series_id = connection.scalar(select(series.c.id).limit(1))
        connection.execute(
            delete(revisiones_observacion).where(
                revisiones_observacion.c.serie_id == series_id,
                revisiones_observacion.c.periodo.in_([date(2026, 1, 1), date(2026, 2, 1)]),
            )
        )
        connection.execute(
            delete(observaciones).where(
                observaciones.c.serie_id == series_id,
                observaciones.c.periodo.in_([date(2026, 1, 1), date(2026, 2, 1)]),
            )
        )
        connection.execute(
            insert(ejecuciones_etl).values(
                id=execution_id,
                modo="bootstrap",
                iniciada_en=datetime.now(UTC),
                estado="iniciada",
                version_catalogo="test",
            )
        )
        file_id = connection.scalar(
            insert(archivos_fuente)
            .values(
                ejecucion_id=execution_id,
                geografia_id="mx",
                sha256="a" * 64,
                ruta_relativa="raw/test.csv",
            )
            .returning(archivos_fuente.c.id)
        )
        connection.execute(
            insert(observaciones),
            [
                {
                    "serie_id": series_id,
                    "periodo": date(2026, 1, 1),
                    "valor": Decimal("123.456789"),
                    "archivo_fuente_id": file_id,
                    "ejecucion_id": execution_id,
                },
                {
                    "serie_id": series_id,
                    "periodo": date(2026, 2, 1),
                    "valor": None,
                    "archivo_fuente_id": file_id,
                    "ejecucion_id": execution_id,
                },
            ],
        )
        values = (
            connection.execute(
                select(observaciones.c.valor)
                .where(
                    observaciones.c.serie_id == series_id,
                    observaciones.c.periodo.in_([date(2026, 1, 1), date(2026, 2, 1)]),
                )
                .order_by(observaciones.c.periodo)
            )
            .scalars()
            .all()
        )
        assert values == [Decimal("123.456789"), None]

        with pytest.raises(IntegrityError):
            with connection.begin_nested():
                connection.execute(
                    insert(observaciones).values(
                        serie_id=series_id,
                        periodo=date(2026, 2, 2),
                        valor=Decimal("1.000000"),
                        archivo_fuente_id=file_id,
                        ejecucion_id=execution_id,
                    )
                )

        connection.execute(
            insert(revisiones_observacion).values(
                serie_id=series_id,
                periodo=date(2026, 1, 1),
                valor_anterior=Decimal("120.000000"),
                valor_nuevo=Decimal("123.456789"),
                ejecucion_id=execution_id,
                archivo_fuente_id=file_id,
                registrada_en=datetime.now(UTC),
            )
        )
        with pytest.raises(IntegrityError):
            with connection.begin_nested():
                connection.execute(
                    insert(revisiones_observacion).values(
                        serie_id=series_id,
                        periodo=date(2030, 4, 1),
                        valor_anterior=None,
                        valor_nuevo=Decimal("123.456789"),
                        ejecucion_id=execution_id,
                        archivo_fuente_id=file_id,
                        registrada_en=datetime.now(UTC),
                    )
                )

        with pytest.raises(IntegrityError):
            with connection.begin_nested():
                connection.execute(
                    insert(observaciones).values(
                        serie_id=series_id,
                        periodo=date(2030, 3, 1),
                        valor=Decimal("-1.000000"),
                        archivo_fuente_id=file_id,
                        ejecucion_id=execution_id,
                    )
                )
