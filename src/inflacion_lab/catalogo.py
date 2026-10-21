"""Catálogo offline de las series publicadas del INPC."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

DEFAULT_CATALOG_PATH = Path("config/series.yml")
EXPECTED_LEVELS = {"nacional": 1, "entidad": 32, "ciudad": 55}


class CatalogError(ValueError):
    """Indica que el catálogo no cumple el contrato de identidades."""


@dataclass(frozen=True)
class Rubro:
    id: str
    etiqueta_fuente: str
    orden: int


@dataclass(frozen=True)
class Serie:
    rubro_id: str
    id_serie_inegi: str
    etiqueta_fuente: str
    frecuencia: str
    clasificacion: str
    referencia_indice: str
    inicio_cobertura: str
    verificado_en: str


@dataclass(frozen=True)
class Geografia:
    id: str
    nivel: str
    nombre: str
    id_estructura: str
    url_fuente: str
    series: tuple[Serie, ...]
    entidad: str | None = None


@dataclass(frozen=True)
class Catalogo:
    rubros: tuple[Rubro, ...]
    geografias: tuple[Geografia, ...]

    @property
    def total_series(self) -> int:
        return sum(len(geografia.series) for geografia in self.geografias)


def load_catalog(path: Path = DEFAULT_CATALOG_PATH) -> Catalogo:
    """Carga y valida el catálogo sin red ni otros servicios."""
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except OSError as error:
        raise CatalogError(
            f"No se pudo leer el catálogo {path}: {error.strerror or error}"
        ) from error
    except yaml.YAMLError as error:
        raise CatalogError(f"El catálogo {path} no es YAML válido: {error}") from error

    root = _mapping(raw, "raíz")
    rubros = tuple(
        _parse_rubro(item, index)
        for index, item in enumerate(_sequence(root.get("rubros"), "rubros"), start=1)
    )
    geografias = tuple(
        _parse_geografia(item, index)
        for index, item in enumerate(_sequence(root.get("geografias"), "geografias"), start=1)
    )
    catalog = Catalogo(rubros=rubros, geografias=geografias)
    _validate(catalog)
    return catalog


def _parse_rubro(raw: Any, position: int) -> Rubro:
    item = _mapping(raw, f"rubro {position}")
    return Rubro(
        id=_text(item.get("id"), f"rubro {position}.id"),
        etiqueta_fuente=_text(item.get("etiqueta_fuente"), f"rubro {position}.etiqueta_fuente"),
        orden=_positive_int(item.get("orden"), f"rubro {position}.orden"),
    )


def _parse_geografia(raw: Any, position: int) -> Geografia:
    item = _mapping(raw, f"geografía {position}")
    series = tuple(
        _parse_serie(series, position, series_position)
        for series_position, series in enumerate(
            _sequence(item.get("series"), f"geografía {position}.series"), start=1
        )
    )
    entidad = item.get("entidad")
    if entidad is not None:
        entidad = _text(entidad, f"geografía {position}.entidad")
    return Geografia(
        id=_text(item.get("id"), f"geografía {position}.id"),
        nivel=_text(item.get("nivel"), f"geografía {position}.nivel"),
        nombre=_text(item.get("nombre"), f"geografía {position}.nombre"),
        id_estructura=_text(item.get("id_estructura"), f"geografía {position}.id_estructura"),
        url_fuente=_text(item.get("url_fuente"), f"geografía {position}.url_fuente"),
        series=series,
        entidad=entidad,
    )


def _parse_serie(raw: Any, geography_position: int, series_position: int) -> Serie:
    item = _mapping(raw, f"geografía {geography_position}.serie {series_position}")
    prefix = f"geografía {geography_position}.serie {series_position}"
    return Serie(
        rubro_id=_text(item.get("rubro_id"), f"{prefix}.rubro_id"),
        id_serie_inegi=_text(item.get("id_serie_inegi"), f"{prefix}.id_serie_inegi"),
        etiqueta_fuente=_text(item.get("etiqueta_fuente"), f"{prefix}.etiqueta_fuente"),
        frecuencia=_text(item.get("frecuencia"), f"{prefix}.frecuencia"),
        clasificacion=_text(item.get("clasificacion"), f"{prefix}.clasificacion"),
        referencia_indice=_text(item.get("referencia_indice"), f"{prefix}.referencia_indice"),
        inicio_cobertura=_text(item.get("inicio_cobertura"), f"{prefix}.inicio_cobertura"),
        verificado_en=_text(item.get("verificado_en"), f"{prefix}.verificado_en"),
    )


def _validate(catalog: Catalogo) -> None:
    if len(catalog.rubros) != 9:
        raise CatalogError(f"Se esperaban 9 rubros; se recibieron {len(catalog.rubros)}.")
    rubro_ids = [rubro.id for rubro in catalog.rubros]
    _unique(rubro_ids, "IDs de rubro")
    if sorted(rubro.orden for rubro in catalog.rubros) != list(range(1, 10)):
        raise CatalogError("Los órdenes de rubro deben abarcar del 1 al 9 sin repetirse.")

    if len(catalog.geografias) != sum(EXPECTED_LEVELS.values()):
        raise CatalogError(f"Se esperaban 88 geografías; se recibieron {len(catalog.geografias)}.")
    _unique([geografia.id for geografia in catalog.geografias], "IDs de geografía")
    _unique([geografia.id_estructura for geografia in catalog.geografias], "IDs de estructura")
    levels = Counter(geografia.nivel for geografia in catalog.geografias)
    if levels != Counter(EXPECTED_LEVELS):
        raise CatalogError(
            f"Los niveles deben ser {EXPECTED_LEVELS}; se recibieron {dict(levels)}."
        )

    provider_ids: list[str] = []
    expected_rubros = set(rubro_ids)
    for geografia in catalog.geografias:
        if len(geografia.series) != 9:
            raise CatalogError(
                f"{geografia.id} debe contener 9 series; contiene {len(geografia.series)}."
            )
        series_rubros = [serie.rubro_id for serie in geografia.series]
        if set(series_rubros) != expected_rubros or len(set(series_rubros)) != 9:
            raise CatalogError(f"{geografia.id} no contiene exactamente una serie por rubro.")
        for serie in geografia.series:
            if serie.frecuencia != "mensual":
                raise CatalogError(f"{geografia.id}/{serie.rubro_id} no tiene frecuencia mensual.")
            if not serie.id_serie_inegi.isdigit():
                raise CatalogError(
                    f"{geografia.id}/{serie.rubro_id} tiene un ID INEGI no numérico."
                )
            provider_ids.append(serie.id_serie_inegi)
    _unique(provider_ids, "IDs de serie INEGI")
    if catalog.total_series != 792:
        raise CatalogError(f"Se esperaban 792 series; se recibieron {catalog.total_series}.")


def _unique(values: Sequence[str], label: str) -> None:
    duplicates = sorted(value for value, count in Counter(values).items() if count > 1)
    if duplicates:
        raise CatalogError(f"{label} repetidos: {', '.join(duplicates[:3])}.")


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise CatalogError(f"{label} debe ser un objeto YAML.")
    return value


def _sequence(value: Any, label: str) -> Sequence[Any]:
    if not isinstance(value, list):
        raise CatalogError(f"{label} debe ser una lista YAML.")
    return value


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CatalogError(f"{label} debe ser texto no vacío.")
    return value


def _positive_int(value: Any, label: str) -> int:
    if not isinstance(value, int) or value <= 0:
        raise CatalogError(f"{label} debe ser un entero positivo.")
    return value
