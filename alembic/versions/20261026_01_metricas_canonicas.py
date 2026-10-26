"""Añade las vistas canónicas de índices y tasas del INPC.

Revision ID: 20261026_01
Revises: 20261025_01
Create Date: 2026-10-26 00:00:00
"""

from __future__ import annotations

from alembic import op

revision = "20261026_01"
down_revision = "20261025_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Expone niveles y tasas sin sustituir un mes ausente por otra fila."""
    op.execute(
        """
        CREATE VIEW metricas_indice AS
        SELECT
            observaciones.serie_id,
            observaciones.periodo,
            observaciones.valor AS indice,
            CASE
                WHEN observaciones.valor IS NULL THEN 'sin_valor_fuente'
                ELSE 'disponible'
            END AS indice_estado
        FROM observaciones
        """
    )
    op.execute(
        """
        CREATE VIEW metricas_tasas AS
        SELECT
            actual.serie_id,
            actual.periodo,
            actual.indice,
            actual.indice_estado,
            CASE
                WHEN actual.indice IS NULL THEN NULL
                WHEN mes_anterior.indice IS NULL THEN NULL
                ELSE 100 * (actual.indice / mes_anterior.indice - 1)
            END AS mensual,
            CASE
                WHEN actual.indice IS NULL THEN 'sin_valor_fuente'
                WHEN mes_anterior.indice IS NULL THEN 'sin_denominador'
                ELSE 'disponible'
            END AS mensual_estado,
            CASE
                WHEN actual.indice IS NULL THEN NULL
                WHEN anio_anterior.indice IS NULL THEN NULL
                ELSE 100 * (actual.indice / anio_anterior.indice - 1)
            END AS anual,
            CASE
                WHEN actual.indice IS NULL THEN 'sin_valor_fuente'
                WHEN anio_anterior.indice IS NULL THEN 'sin_denominador'
                ELSE 'disponible'
            END AS anual_estado
        FROM metricas_indice AS actual
        LEFT JOIN metricas_indice AS mes_anterior
            ON mes_anterior.serie_id = actual.serie_id
            AND mes_anterior.periodo = actual.periodo - INTERVAL '1 month'
        LEFT JOIN metricas_indice AS anio_anterior
            ON anio_anterior.serie_id = actual.serie_id
            AND anio_anterior.periodo = actual.periodo - INTERVAL '1 year'
        """
    )


def downgrade() -> None:
    """Elimina las vistas derivadas antes de las tablas que consumen."""
    op.execute("DROP VIEW metricas_tasas")
    op.execute("DROP VIEW metricas_indice")
