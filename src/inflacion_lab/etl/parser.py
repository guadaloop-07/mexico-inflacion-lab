"""Parser estricto del CSV vertical publicado por el INPC."""

from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation

from ..catalogo import Geografia

MONTHS = {
    "Ene": 1,
    "Feb": 2,
    "Mar": 3,
    "Abr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Ago": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dic": 12,
}
PERIOD_RE = re.compile(r"^(Ene|Feb|Mar|Abr|May|Jun|Jul|Ago|Sep|Oct|Nov|Dic) (\d{4})$")


class ParseError(ValueError):
    """Indica una exportación que no puede identificarse de forma inequívoca."""


@dataclass(frozen=True)
class Observation:
    serie_id: str
    rubro_id: str
    periodo: date
    valor: Decimal | None


def parse_csv(payload: bytes, geografia: Geografia) -> tuple[Observation, ...]:
    """Convierte un CSV de una geografía a observaciones tipadas y validadas."""
    try:
        rows = list(csv.reader(io.StringIO(payload.decode("iso-8859-1"))))
    except (UnicodeDecodeError, csv.Error) as error:
        raise ParseError(f"{geografia.id}: CSV ilegible: {error}.") from error
    header_index = next(
        (index for index, row in enumerate(rows) if row and row[0].strip() == "Fecha"), None
    )
    if header_index is None:
        raise ParseError(f"{geografia.id}: no se encontró la fila de IDs 'Fecha'.")
    ids = [value.strip() for value in rows[header_index][1:]]
    expected = {serie.id_serie_inegi: serie for serie in geografia.series}
    if len(ids) != len(set(ids)):
        raise ParseError(f"{geografia.id}: el CSV contiene columnas de serie duplicadas.")
    unknown = sorted(set(ids) - set(expected))
    missing = sorted(set(expected) - set(ids))
    if unknown or missing or len(ids) != len(expected):
        details = []
        if unknown:
            details.append(f"desconocidas: {', '.join(unknown)}")
        if missing:
            details.append(f"faltantes: {', '.join(missing)}")
        raise ParseError(f"{geografia.id}: columnas de serie inválidas ({'; '.join(details)}).")

    observations: list[Observation] = []
    seen: set[tuple[str, date]] = set()
    for row in rows[header_index + 1 :]:
        if not row or not any(value.strip() for value in row):
            continue
        match = PERIOD_RE.fullmatch(row[0].strip())
        if match is None:
            raise ParseError(f"{geografia.id}: periodo desconocido {row[0]!r}.")
        if len(row) != len(ids) + 1:
            raise ParseError(f"{geografia.id}: fila {row[0]!r} con un número inválido de columnas.")
        periodo = date(int(match.group(2)), MONTHS[match.group(1)], 1)
        for serie_id, token in zip(ids, row[1:], strict=True):
            key = (serie_id, periodo)
            if key in seen:
                raise ParseError(
                    f"{geografia.id}: clave de observación duplicada {serie_id}/{periodo}."
                )
            seen.add(key)
            observations.append(
                Observation(
                    serie_id=serie_id,
                    rubro_id=expected[serie_id].rubro_id,
                    periodo=periodo,
                    valor=_decimal(token, geografia.id, serie_id, periodo),
                )
            )
    if not observations:
        raise ParseError(f"{geografia.id}: el CSV no contiene observaciones.")
    return tuple(observations)


def _decimal(token: str, geography_id: str, serie_id: str, periodo: date) -> Decimal:
    value = token.strip()
    if not value:
        raise ParseError(f"{geography_id}: valor vacío para {serie_id}/{periodo}.")
    try:
        decimal = Decimal(value)
    except InvalidOperation as error:
        raise ParseError(
            f"{geography_id}: valor no numérico {value!r} para {serie_id}/{periodo}."
        ) from error
    if not decimal.is_finite():
        raise ParseError(f"{geography_id}: valor no finito para {serie_id}/{periodo}.")
    return decimal
