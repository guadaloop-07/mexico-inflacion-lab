"""Pruebas de publicación transaccional sobre PostgreSQL real."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from inflacion_lab.catalogo import load_catalog
from inflacion_lab.db.carga import (
    WriterBusyError,
    acquire_writer_lock,
    create_execution,
    publish,
    release_writer_lock,
)
from inflacion_lab.db.tablas import observaciones, revisiones_observacion, series
from inflacion_lab.etl.ejecucion import SourceFile
from inflacion_lab.etl.parser import Observation, parse_csv

pytestmark = pytest.mark.integration


def _source(rows: tuple[Observation, ...]) -> SourceFile:
    return SourceFile("mx", "mx.csv", "b" * 64, {"origen": "fixture"}, rows)


def _mexico_rows() -> tuple[Observation, ...]:
    catalog = load_catalog()
    return parse_csv(
        Path("tests/fixtures/inegi/mexico-2024-2026.csv").read_bytes(), catalog.geografias[0]
    )


def _publish(migrated_engine, rows: tuple[Observation, ...]) -> None:
    catalog = load_catalog()
    execution_id = uuid4()
    with migrated_engine.connect() as connection:
        create_execution(connection, execution_id, "bootstrap", "test")
        with connection.begin():
            publish(
                connection,
                execution_id=execution_id,
                catalog=catalog,
                files=(_source(rows),),
                raw_dir=Path("data/raw/test"),
            )


def test_identical_publish_is_idempotent_and_correction_is_audited(migrated_engine) -> None:
    rows = _mexico_rows()
    _publish(migrated_engine, rows)
    with migrated_engine.connect() as connection:
        before = connection.scalar(select(func.count()).select_from(observaciones))
        revisions = connection.scalar(select(func.count()).select_from(revisiones_observacion))
        published = connection.scalar(
            select(observaciones.c.valor)
            .join_from(observaciones, series)
            .where(
                series.c.id_serie_inegi == rows[0].serie_id,
                observaciones.c.periodo == rows[0].periodo,
            )
        )
        assert published is not None
        assert published.as_tuple().exponent == -12
    _publish(migrated_engine, rows)
    with migrated_engine.connect() as connection:
        assert connection.scalar(select(func.count()).select_from(observaciones)) == before
        assert (
            connection.scalar(select(func.count()).select_from(revisiones_observacion)) == revisions
        )

    corrected = list(rows)
    corrected[0] = Observation(
        corrected[0].serie_id,
        corrected[0].rubro_id,
        corrected[0].periodo,
        Decimal("999.000000"),
    )
    _publish(migrated_engine, tuple(corrected))
    with migrated_engine.connect() as connection:
        assert (
            connection.scalar(select(func.count()).select_from(revisiones_observacion))
            == revisions + 1
        )
        revision = connection.execute(
            select(revisiones_observacion.c.valor_anterior, revisiones_observacion.c.valor_nuevo)
            .order_by(revisiones_observacion.c.id.desc())
            .limit(1)
        ).one()
        assert revision.valor_nuevo == Decimal("999.000000")


def test_invalid_final_row_reverts_all_observation_changes(migrated_engine) -> None:
    rows = _mexico_rows()
    _publish(migrated_engine, rows)
    with migrated_engine.connect() as connection:
        before = connection.scalar(select(func.count()).select_from(observaciones))
    broken = list(rows)
    broken[-1] = Observation(
        broken[-1].serie_id, broken[-1].rubro_id, broken[-1].periodo, Decimal("-1")
    )
    with pytest.raises(IntegrityError):
        _publish(migrated_engine, tuple(broken))
    with migrated_engine.connect() as connection:
        assert connection.scalar(select(func.count()).select_from(observaciones)) == before


def test_writer_lock_excludes_a_second_connection(migrated_engine) -> None:
    first = migrated_engine.connect()
    second = migrated_engine.connect()
    try:
        acquire_writer_lock(first)
        with pytest.raises(WriterBusyError):
            acquire_writer_lock(second)
    finally:
        release_writer_lock(first)
        first.close()
        second.close()
