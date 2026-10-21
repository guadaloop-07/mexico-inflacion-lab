from __future__ import annotations

import csv
import hashlib
from pathlib import Path

import pytest
import yaml

from inflacion_lab.catalogo import CatalogError, load_catalog

CATALOG_PATH = Path("config/series.yml")
FIXTURE_DIRECTORY = Path("tests/fixtures/inegi")


def _write_catalog(tmp_path: Path, mutate: object) -> Path:
    raw = yaml.safe_load(CATALOG_PATH.read_text(encoding="utf-8"))
    mutate(raw)
    path = tmp_path / "series.yml"
    path.write_text(yaml.safe_dump(raw, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return path


def test_production_catalog_has_all_expected_series() -> None:
    catalog = load_catalog(CATALOG_PATH)

    assert len(catalog.geografias) == 88
    assert len(catalog.rubros) == 9
    assert catalog.total_series == 792
    assert catalog.geografias[0].series[0].id_serie_inegi == "865586"


def test_official_fixtures_match_their_manifest() -> None:
    manifest = yaml.safe_load((FIXTURE_DIRECTORY / "manifest.yml").read_text(encoding="utf-8"))

    for fixture in manifest["fixtures"]:
        path = FIXTURE_DIRECTORY / fixture["archivo"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == fixture["sha256"]
        with path.open(encoding="iso-8859-1", newline="") as source:
            rows = list(csv.reader(source))
        id_row = next(row for row in rows if row and row[0] == "Fecha")
        assert id_row[1:] == fixture["ids_serie_inegi"]
        observations = [
            row
            for row in rows
            if row
            and row[0][:3]
            in {"Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"}
        ]
        assert len(observations) >= 24


def test_catalog_rejects_duplicate_provider_series(tmp_path: Path) -> None:
    path = _write_catalog(
        tmp_path,
        lambda raw: raw["geografias"][1]["series"].__setitem__(
            0, {**raw["geografias"][1]["series"][0], "id_serie_inegi": "865586"}
        ),
    )

    with pytest.raises(CatalogError, match="IDs de serie INEGI repetidos"):
        load_catalog(path)


def test_catalog_rejects_missing_geography(tmp_path: Path) -> None:
    path = _write_catalog(tmp_path, lambda raw: raw["geografias"].pop())

    with pytest.raises(CatalogError, match="Se esperaban 88 geografías"):
        load_catalog(path)


def test_catalog_rejects_missing_rubro(tmp_path: Path) -> None:
    path = _write_catalog(tmp_path, lambda raw: raw["rubros"].pop())

    with pytest.raises(CatalogError, match="Se esperaban 9 rubros"):
        load_catalog(path)
