"""Orquestación de una extracción completa sin publicar observaciones."""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from uuid import UUID, uuid4

from ..catalogo import Catalogo
from ..config import Settings
from .cliente import DEFAULT_EXPORT_URL, InpcClient, TransportError
from .parser import Observation, ParseError, parse_csv


class FetchRunError(RuntimeError):
    """Resume fallos por archivo de una ejecución que no puede ser exitosa."""


class EtlRunError(RuntimeError):
    """El lote se conservó, pero no pudo convertirse en una publicación."""


@dataclass(frozen=True)
class SourceFile:
    geografia_id: str
    ruta: str
    sha256: str
    parametros: dict[str, str]
    rows: tuple[Observation, ...]


@dataclass(frozen=True)
class FetchResult:
    run_dir: Path
    geografias_ok: int
    series_recibidas: int
    observaciones: int
    files: tuple[SourceFile, ...] = ()


def fetch_catalog(
    catalogo: Catalogo,
    *,
    data_dir: Path,
    start_year: int = 2018,
    end_year: int | None = None,
    client: InpcClient | None = None,
    execution_id: UUID | None = None,
) -> FetchResult:
    """Descarga, conserva y valida las 88 geografías antes de declarar éxito."""
    end_year = end_year or datetime.now(UTC).year
    run = _RawRun(
        data_dir / "raw" / str(execution_id or uuid4()), start_year, end_year, catalogo.total_series
    )
    transport = client or InpcClient()
    owns_client = client is None
    observations: list[Observation] = []
    series: set[str] = set()
    failures: list[str] = []
    files: list[SourceFile] = []
    try:
        for position, geografia in enumerate(catalogo.geografias, start=1):
            relative_path: str | None = None
            digest: str | None = None
            try:
                payload = transport.fetch(geografia, start_year, end_year)
                relative_path, digest = run.write(geografia.id, payload)
                parsed = parse_csv(payload, geografia)
                parameters = transport.manifest_parameters(geografia, start_year, end_year)
                files.append(SourceFile(geografia.id, relative_path, digest, parameters, parsed))
                observations.extend(parsed)
                series.update(item.serie_id for item in parsed)
                run.record_success(
                    geografia.id,
                    relative_path,
                    digest,
                    len(parsed),
                    parameters,
                )
            except (TransportError, ParseError, OSError, ValueError) as error:
                failures.append(f"{geografia.id}: {error}")
                run.record_failure(geografia.id, str(error), relative_path, digest)
            if position < len(catalogo.geografias):
                transport.pause_between_locations()
    except BaseException:
        failures.append("Extracción interrumpida antes de completar el catálogo.")
        raise
    finally:
        if owns_client:
            transport.close()
        if not failures and len(series) != catalogo.total_series:
            failures.append(f"Se recibieron {len(series)} de {catalogo.total_series} series.")
        run.finish(failures)
    if failures:
        raise FetchRunError(
            f"La extracción no es publicable: {len(failures)} de {len(catalogo.geografias)} "
            f"archivos fallaron. "
            f"Manifiesto: {run.path / 'manifest.json'}."
        )
    return FetchResult(
        run.path, len(catalogo.geografias), len(series), len(observations), tuple(files)
    )


def run_catalog(catalog: Catalogo, settings: Settings, *, mode: str) -> FetchResult:
    """Descarga y publica el catálogo completo, conservando la versión anterior ante un fallo."""
    from ..db.carga import (
        acquire_writer_lock,
        bootstrap_exists,
        create_execution,
        mark_failed,
        publish,
        release_writer_lock,
    )
    from ..db.conexion import create_engine
    from .validacion import validate_batch

    execution_id = uuid4()
    engine = create_engine(settings.database_url("etl"))
    connection = engine.connect()
    locked = False
    try:
        create_execution(connection, execution_id, mode, _catalog_version(catalog))
        acquire_writer_lock(connection)
        locked = True
        if mode == "refresh" and not bootstrap_exists(connection):
            raise EtlRunError("refresh exige un bootstrap exitoso previo.")
        connection.commit()
        start_year = 2018 if mode in {"bootstrap", "reconcile"} else _refresh_start().year
        client = InpcClient(settings.inpc_export_url or DEFAULT_EXPORT_URL)
        try:
            result = fetch_catalog(
                catalog,
                data_dir=settings.data_dir,
                start_year=start_year,
                client=client,
                execution_id=execution_id,
            )
        finally:
            client.close()
        start = date(start_year, 1, 1) if mode != "refresh" else _refresh_start()
        validate_batch(
            catalog, tuple(row for source in result.files for row in source.rows), start=start
        )
        with connection.begin():
            publish(
                connection,
                execution_id=execution_id,
                catalog=catalog,
                files=result.files,
                raw_dir=result.run_dir,
            )
        return result
    except Exception as error:
        mark_failed(engine, execution_id, str(error))
        raise EtlRunError(str(error)) from error
    finally:
        if locked:
            release_writer_lock(connection)
        connection.close()
        engine.dispose()


def _refresh_start(today: date | None = None) -> date:
    today = today or date.today()
    last_closed = date(
        today.year if today.month > 1 else today.year - 1, (today.month - 2) % 12 + 1, 1
    )
    month = last_closed.month - 24
    return date(last_closed.year + month // 12, month % 12 + 1, 1)


def _catalog_version(catalog: Catalogo) -> str:
    material = "|".join(
        f"{geography.id}:{series.id_serie_inegi}"
        for geography in catalog.geografias
        for series in geography.series
    )
    return hashlib.sha256(material.encode()).hexdigest()[:16]


class _RawRun:
    def __init__(self, path: Path, start_year: int, end_year: int, expected_series: int) -> None:
        self.path = path
        self.manifest: dict[str, object] = {
            "ejecucion": path.name,
            "inicio_utc": datetime.now(UTC).isoformat(),
            "solicitud": {
                "inicio": start_year,
                "fin": end_year,
                "series_esperadas": expected_series,
            },
            "archivos": [],
        }

    def write(self, geography_id: str, payload: bytes) -> tuple[str, str]:
        self.path.mkdir(parents=True, exist_ok=True)
        filename = f"{geography_id}.csv"
        target = self.path / filename
        temporary = target.with_suffix(".csv.tmp")
        with temporary.open("wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(target)
        return filename, hashlib.sha256(payload).hexdigest()

    def record_success(
        self,
        geography_id: str,
        path: str,
        digest: str,
        observations: int,
        parameters: dict[str, str],
    ) -> None:
        files = self.manifest["archivos"]
        assert isinstance(files, list)
        files.append(
            {
                "geografia_id": geography_id,
                "ruta": path,
                "sha256": digest,
                "observaciones": observations,
                "parametros": parameters,
                "estado": "válido",
            }
        )

    def record_failure(
        self,
        geography_id: str,
        error: str,
        path: str | None = None,
        digest: str | None = None,
    ) -> None:
        files = self.manifest["archivos"]
        assert isinstance(files, list)
        entry: dict[str, object] = {
            "geografia_id": geography_id,
            "estado": "fallido",
            "error": error,
        }
        if path is not None and digest is not None:
            entry.update({"ruta": path, "sha256": digest})
        files.append(entry)

    def finish(self, failures: list[str]) -> None:
        self.path.mkdir(parents=True, exist_ok=True)
        self.manifest["fin_utc"] = datetime.now(UTC).isoformat()
        self.manifest["estado"] = "fallido" if failures else "válido"
        target = self.path / "manifest.json"
        temporary = target.with_suffix(".json.tmp")
        temporary.write_text(
            json.dumps(self.manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        temporary.replace(target)
