"""Publicación atómica de un lote INPC ya validado."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from sqlalchemy import Connection, Engine, func, insert, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert

from ..catalogo import Catalogo
from ..etl.ejecucion import SourceFile
from .catalogo import register_catalog
from .tablas import archivos_fuente, ejecuciones_etl, observaciones, revisiones_observacion, series

LOCK_ID = 4179202605


class WriterBusyError(RuntimeError):
    """Otro proceso ETL mantiene el bloqueo de publicación."""


def create_execution(
    connection: Connection, execution_id: UUID, mode: str, catalog_version: str
) -> None:
    connection.execute(
        insert(ejecuciones_etl).values(
            id=execution_id,
            modo=mode,
            iniciada_en=datetime.now(UTC),
            estado="iniciada",
            version_catalogo=catalog_version,
        )
    )
    connection.commit()


def acquire_writer_lock(connection: Connection) -> None:
    if not connection.scalar(select(func.pg_try_advisory_lock(LOCK_ID))):
        raise WriterBusyError("Otra ejecución ETL está publicando datos.")


def release_writer_lock(connection: Connection) -> None:
    connection.execute(select(func.pg_advisory_unlock(LOCK_ID)))


def mark_failed(engine: Engine, execution_id: UUID, error: str) -> None:
    with engine.begin() as connection:
        connection.execute(
            update(ejecuciones_etl)
            .where(ejecuciones_etl.c.id == execution_id)
            .values(
                estado="fallida", finalizada_en=datetime.now(UTC), error_sanitizado=error[:2000]
            )
        )


def bootstrap_exists(connection: Connection) -> bool:
    return bool(
        connection.scalar(
            select(ejecuciones_etl.c.id)
            .where(ejecuciones_etl.c.modo == "bootstrap", ejecuciones_etl.c.estado == "exitosa")
            .limit(1)
        )
    )


def publish(
    connection: Connection,
    *,
    execution_id: UUID,
    catalog: Catalogo,
    files: tuple[SourceFile, ...],
    raw_dir: Path,
) -> int:
    """Registra originales, actualiza índices y audita solo valores modificados."""
    register_catalog(connection, catalog)
    series_ids = dict(connection.execute(select(series.c.id_serie_inegi, series.c.id)).all())
    rows: list[dict[str, object]] = []
    for source in files:
        periods = [item.periodo for item in source.rows]
        file_id = connection.scalar(
            insert(archivos_fuente)
            .values(
                ejecucion_id=execution_id,
                geografia_id=source.geografia_id,
                sha256=source.sha256,
                ruta_relativa=str(Path("raw") / raw_dir.name / source.ruta),
                parametros=source.parametros,
                cobertura_desde=min(periods),
                cobertura_hasta=max(periods),
            )
            .returning(archivos_fuente.c.id)
        )
        assert file_id is not None
        rows.extend(
            {
                "serie_id": series_ids[item.serie_id],
                "periodo": item.periodo,
                "valor": item.valor,
                "archivo_fuente_id": file_id,
                "ejecucion_id": execution_id,
            }
            for item in source.rows
        )

    keys = {(row["serie_id"], row["periodo"]) for row in rows}
    previous = {
        (row.serie_id, row.periodo): row.valor
        for row in connection.execute(
            select(observaciones.c.serie_id, observaciones.c.periodo, observaciones.c.valor)
        ).all()
        if (row.serie_id, row.periodo) in keys
    }
    statement = pg_insert(observaciones).values(rows)
    connection.execute(
        statement.on_conflict_do_update(
            index_elements=[observaciones.c.serie_id, observaciones.c.periodo],
            set_={
                "valor": statement.excluded.valor,
                "archivo_fuente_id": statement.excluded.archivo_fuente_id,
                "ejecucion_id": statement.excluded.ejecucion_id,
            },
            where=observaciones.c.valor.is_distinct_from(statement.excluded.valor),
        )
    )
    changes = [
        row
        for row in rows
        if (row["serie_id"], row["periodo"]) in previous
        and previous[(row["serie_id"], row["periodo"])] != row["valor"]
    ]
    if changes:
        connection.execute(
            insert(revisiones_observacion),
            [
                {
                    "serie_id": row["serie_id"],
                    "periodo": row["periodo"],
                    "valor_anterior": previous[(row["serie_id"], row["periodo"])],
                    "valor_nuevo": row["valor"],
                    "ejecucion_id": execution_id,
                    "archivo_fuente_id": row["archivo_fuente_id"],
                    "registrada_en": datetime.now(UTC),
                }
                for row in changes
            ],
        )
    connection.execute(
        update(ejecuciones_etl)
        .where(ejecuciones_etl.c.id == execution_id)
        .values(
            estado="exitosa",
            finalizada_en=datetime.now(UTC),
            series_recibidas=catalog.total_series,
            observaciones_recibidas=len(rows),
        )
    )
    return len(rows)
