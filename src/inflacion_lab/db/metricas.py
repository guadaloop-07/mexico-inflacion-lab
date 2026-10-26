"""Consultas canónicas de índices y variaciones del INPC."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Literal

from sqlalchemy import Connection, text

Medida = Literal["indice", "mensual", "anual"]
EstadoMetrica = Literal["disponible", "no_publicado", "sin_valor_fuente", "sin_denominador"]

_UNIDADES: dict[Medida, str] = {
    "indice": "puntos_indice",
    "mensual": "porcentaje",
    "anual": "porcentaje",
}


@dataclass(frozen=True)
class ResultadoMetrica:
    """Un valor mensual con su unidad y causa explícita cuando falta."""

    periodo: date
    valor: Decimal | None
    estado: EstadoMetrica
    unidad: str


@dataclass(frozen=True)
class ResultadoRazon:
    """Resultado de comparar dos niveles del índice de la misma serie."""

    inicio: date
    fin: date
    razon: Decimal | None
    variacion: Decimal | None
    estado: EstadoMetrica


@dataclass(frozen=True)
class ResultadoDiferencia:
    """Diferencia de tasas, expresada en puntos porcentuales."""

    periodo: date
    valor: Decimal | None
    estado: EstadoMetrica
    unidad: str = "puntos_porcentuales"


def serie_metricas(
    connection: Connection,
    *,
    serie_id: int,
    medida: Medida,
    desde: date | None = None,
    hasta: date | None = None,
) -> tuple[ResultadoMetrica, ...]:
    """Devuelve una medida calculada antes de aplicar el intervalo solicitado."""
    if medida not in _UNIDADES:
        raise ValueError(f"Medida desconocida: {medida}")
    column = medida
    state_column = f"{medida}_estado"
    rows = connection.execute(
        text(
            f"""
            SELECT periodo, {column} AS valor, {state_column} AS estado
            FROM metricas_tasas
            WHERE serie_id = :serie_id
              AND (:desde IS NULL OR periodo >= :desde)
              AND (:hasta IS NULL OR periodo <= :hasta)
            ORDER BY periodo
            """
        ),
        {"serie_id": serie_id, "desde": desde, "hasta": hasta},
    ).all()
    return tuple(
        ResultadoMetrica(row.periodo, row.valor, row.estado, _UNIDADES[medida]) for row in rows
    )


def razon_indices(
    connection: Connection,
    *,
    serie_id: int,
    inicio: date,
    fin: date,
) -> ResultadoRazon:
    """Calcula la razón y variación acumulada entre dos meses exactos."""
    row = connection.execute(
        text(
            """
            SELECT inicio.indice AS indice_inicio, fin.indice AS indice_fin,
                   inicio.indice_estado AS estado_inicio, fin.indice_estado AS estado_fin
            FROM (SELECT CAST(:inicio AS date) AS periodo) AS objetivo
            LEFT JOIN metricas_indice AS inicio
              ON inicio.serie_id = :serie_id AND inicio.periodo = objetivo.periodo
            LEFT JOIN metricas_indice AS fin
              ON fin.serie_id = :serie_id AND fin.periodo = :fin
            """
        ),
        {"serie_id": serie_id, "inicio": inicio, "fin": fin},
    ).one()
    estado = _estado_indices(row.indice_inicio, row.indice_fin, row.estado_inicio, row.estado_fin)
    if estado != "disponible":
        return ResultadoRazon(inicio, fin, None, None, estado)
    assert row.indice_inicio is not None
    assert row.indice_fin is not None
    razon = row.indice_fin / row.indice_inicio
    return ResultadoRazon(inicio, fin, razon, 100 * (razon - 1), "disponible")


def diferencia_tasas(
    connection: Connection,
    *,
    primera_serie_id: int,
    segunda_serie_id: int,
    periodo: date,
    medida: Literal["mensual", "anual"],
) -> ResultadoDiferencia:
    """Resta tasas de un corte común; nunca las interpreta como porcentajes compuestos."""
    value_column = medida
    state_column = f"{medida}_estado"
    row = connection.execute(
        text(
            f"""
            SELECT primera.{value_column} AS primera_valor,
                   segunda.{value_column} AS segunda_valor,
                   primera.{state_column} AS primera_estado,
                   segunda.{state_column} AS segunda_estado
            FROM (SELECT CAST(:periodo AS date) AS periodo) AS objetivo
            LEFT JOIN metricas_tasas AS primera
              ON primera.serie_id = :primera_serie_id AND primera.periodo = objetivo.periodo
            LEFT JOIN metricas_tasas AS segunda
              ON segunda.serie_id = :segunda_serie_id AND segunda.periodo = objetivo.periodo
            """
        ),
        {
            "primera_serie_id": primera_serie_id,
            "segunda_serie_id": segunda_serie_id,
            "periodo": periodo,
        },
    ).one()
    estado = _estado_indices(
        row.primera_valor, row.segunda_valor, row.primera_estado, row.segunda_estado
    )
    if estado != "disponible":
        return ResultadoDiferencia(periodo, None, estado)
    assert row.primera_valor is not None
    assert row.segunda_valor is not None
    return ResultadoDiferencia(periodo, row.primera_valor - row.segunda_valor, "disponible")


def _estado_indices(
    primero: Decimal | None,
    segundo: Decimal | None,
    estado_primero: EstadoMetrica | None,
    estado_segundo: EstadoMetrica | None,
) -> EstadoMetrica:
    """Da prioridad a un nulo explícito de fuente sobre una ausencia de fila."""
    if primero is not None and segundo is not None:
        return "disponible"
    if estado_primero == "sin_valor_fuente" or estado_segundo == "sin_valor_fuente":
        return "sin_valor_fuente"
    return "no_publicado"
