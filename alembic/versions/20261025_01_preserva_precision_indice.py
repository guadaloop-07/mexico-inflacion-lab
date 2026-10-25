"""Preserva las doce posiciones decimales de la exportación del INPC.

Revision ID: 20261025_01
Revises: 20261021_01
Create Date: 2026-10-25 00:00:00
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "20261025_01"
down_revision = "20261021_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Amplía la escala sin modificar los valores ya publicados."""
    op.alter_column("observaciones", "valor", type_=sa.Numeric(18, 12))
    op.alter_column("revisiones_observacion", "valor_anterior", type_=sa.Numeric(18, 12))
    op.alter_column("revisiones_observacion", "valor_nuevo", type_=sa.Numeric(18, 12))


def downgrade() -> None:
    """Restaura la escala inicial para una reversión de desarrollo."""
    op.alter_column("revisiones_observacion", "valor_nuevo", type_=sa.Numeric(18, 6))
    op.alter_column("revisiones_observacion", "valor_anterior", type_=sa.Numeric(18, 6))
    op.alter_column("observaciones", "valor", type_=sa.Numeric(18, 6))
