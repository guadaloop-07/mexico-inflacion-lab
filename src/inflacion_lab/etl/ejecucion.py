"""Orquestación de una extracción completa sin publicar observaciones."""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from ..catalogo import Catalogo
from .cliente import InpcClient, TransportError
from .parser import Observation, ParseError, parse_csv


class FetchRunError(RuntimeError):
    """Resume fallos por archivo de una ejecución que no puede ser exitosa."""


@dataclass(frozen=True)
class FetchResult:
    run_dir: Path
    geografias_ok: int
    series_recibidas: int
    observaciones: int


def fetch_catalog(
    catalogo: Catalogo,
    *,
    data_dir: Path,
    start_year: int = 2018,
    end_year: int | None = None,
    client: InpcClient | None = None,
) -> FetchResult:
    """Descarga, conserva y valida las 88 geografías antes de declarar éxito."""
    end_year = end_year or datetime.now(UTC).year
    run = _RawRun(data_dir / "raw" / str(uuid4()), start_year, end_year, catalogo.total_series)
    transport = client or InpcClient()
    owns_client = client is None
    observations: list[Observation] = []
    series: set[str] = set()
    failures: list[str] = []
    try:
        for position, geografia in enumerate(catalogo.geografias, start=1):
            relative_path: str | None = None
            digest: str | None = None
            try:
                payload = transport.fetch(geografia, start_year, end_year)
                relative_path, digest = run.write(geografia.id, payload)
                parsed = parse_csv(payload, geografia)
                observations.extend(parsed)
                series.update(item.serie_id for item in parsed)
                run.record_success(
                    geografia.id,
                    relative_path,
                    digest,
                    len(parsed),
                    transport.manifest_parameters(geografia, start_year, end_year),
                )
            except (TransportError, ParseError, OSError, ValueError) as error:
                failures.append(f"{geografia.id}: {error}")
                run.record_failure(geografia.id, str(error), relative_path, digest)
            if position < len(catalogo.geografias):
                transport.pause_between_locations()
    finally:
        if owns_client:
            transport.close()
    run.finish(failures)
    if failures:
        raise FetchRunError(
            f"La extracción no es publicable: {len(failures)} de {len(catalogo.geografias)} "
            f"archivos fallaron. Manifiesto: {run.path / 'manifest.json'}."
        )
    if len(series) != catalogo.total_series:
        raise FetchRunError(
            f"La extracción recibió {len(series)} de {catalogo.total_series} series esperadas. "
            f"Manifiesto: {run.path / 'manifest.json'}."
        )
    return FetchResult(run.path, len(catalogo.geografias), len(series), len(observations))


class _RawRun:
    def __init__(self, path: Path, start_year: int, end_year: int, expected_series: int) -> None:
        self.path = path
        self.manifest: dict[str, object] = {
            "ejecucion": path.name,
            "inicio_utc": datetime.now(UTC).isoformat(),
            "solicitud": {"inicio": start_year, "fin": end_year, "series_esperadas": expected_series},
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
        temporary.write_text(json.dumps(self.manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temporary.replace(target)
