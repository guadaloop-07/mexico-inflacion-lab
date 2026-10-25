"""Validación de cobertura antes de que un lote alcance PostgreSQL."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date

from ..catalogo import Catalogo
from .parser import Observation


class ValidationError(ValueError):
    """El lote no representa una publicación completa y consistente."""


@dataclass(frozen=True)
class SeriesReport:
    serie_id: str
    observaciones: int
    con_valor: int
    nulas: int
    desde: date
    hasta: date


@dataclass(frozen=True)
class ValidationReport:
    series: tuple[SeriesReport, ...]
    cutoff: date

    @property
    def observaciones(self) -> int:
        return sum(item.observaciones for item in self.series)


def validate_batch(
    catalog: Catalogo, rows: tuple[Observation, ...], *, start: date
) -> ValidationReport:
    """Exige todas las series, meses consecutivos y un mismo corte publicado."""
    expected = {
        serie.id_serie_inegi for geography in catalog.geografias for serie in geography.series
    }
    grouped: dict[str, list[Observation]] = defaultdict(list)
    for row in rows:
        if row.serie_id not in expected:
            raise ValidationError(f"Serie desconocida en el lote: {row.serie_id}.")
        if row.periodo > _last_closed_month():
            raise ValidationError(
                f"{row.serie_id} contiene un periodo todavía no cerrado: {row.periodo}."
            )
        if row.valor is not None and row.valor <= 0:
            raise ValidationError(f"{row.serie_id}/{row.periodo} tiene un índice no positivo.")
        grouped[row.serie_id].append(row)
    missing = sorted(expected - set(grouped))
    if missing:
        raise ValidationError(
            f"Faltan {len(missing)} series; por ejemplo: {', '.join(missing[:3])}."
        )

    reports: list[SeriesReport] = []
    cutoffs: set[date] = set()
    for serie_id in sorted(expected):
        items = sorted(grouped[serie_id], key=lambda item: item.periodo)
        periods = [item.periodo for item in items]
        if len(periods) != len(set(periods)):
            raise ValidationError(f"{serie_id} contiene meses duplicados.")
        if periods[0] > start:
            raise ValidationError(f"{serie_id} inicia en {periods[0]}, posterior a {start}.")
        _require_consecutive(serie_id, periods)
        cutoffs.add(periods[-1])
        reports.append(
            SeriesReport(
                serie_id,
                len(items),
                sum(item.valor is not None for item in items),
                sum(item.valor is None for item in items),
                periods[0],
                periods[-1],
            )
        )
    if len(cutoffs) != 1:
        raise ValidationError("Las series no comparten el mismo mes de corte.")
    return ValidationReport(tuple(reports), cutoffs.pop())


def _require_consecutive(serie_id: str, periods: list[date]) -> None:
    for previous, current in zip(periods, periods[1:], strict=False):
        expected = _next_month(previous)
        if current != expected:
            raise ValidationError(f"{serie_id} tiene un hueco entre {previous} y {current}.")


def _next_month(value: date) -> date:
    return date(value.year + (value.month == 12), value.month % 12 + 1, 1)


def _last_closed_month(today: date | None = None) -> date:
    today = today or date.today()
    return date(today.year if today.month > 1 else today.year - 1, (today.month - 2) % 12 + 1, 1)
