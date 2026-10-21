"""Crea el esquema inicial de persistencia.

Revision ID: 20261021_01
Revises:
Create Date: 2026-10-21 00:00:00
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "20261021_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Crea las siete tablas y sus índices a partir del contrato compartido."""
    op.create_table(
        "geografias",
        sa.Column("id", sa.String(32), nullable=False),
        sa.Column("nivel", sa.String(16), nullable=False),
        sa.Column("nombre", sa.String(200), nullable=False),
        sa.Column("codigo_fuente", sa.String(64), nullable=False),
        sa.Column("entidad", sa.String(32)),
        sa.Column("url_fuente", sa.Text(), nullable=False),
        sa.CheckConstraint("nivel IN ('nacional', 'entidad', 'ciudad')", name="nivel_valido"),
        sa.PrimaryKeyConstraint("id", name="pk_geografias"),
        sa.UniqueConstraint("codigo_fuente", name="uq_geografias_codigo_fuente"),
    )
    op.create_table(
        "rubros",
        sa.Column("id", sa.String(64), nullable=False),
        sa.Column("etiqueta_fuente", sa.String(200), nullable=False),
        sa.Column("orden", sa.Integer(), nullable=False),
        sa.CheckConstraint("orden > 0", name="orden_positivo"),
        sa.PrimaryKeyConstraint("id", name="pk_rubros"),
        sa.UniqueConstraint("orden", name="uq_rubros_orden"),
    )
    op.create_table(
        "series",
        sa.Column("id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("geografia_id", sa.String(32), nullable=False),
        sa.Column("rubro_id", sa.String(64), nullable=False),
        sa.Column("id_serie_inegi", sa.String(32), nullable=False),
        sa.Column("etiqueta_fuente", sa.String(300), nullable=False),
        sa.Column("frecuencia", sa.String(16), nullable=False),
        sa.Column("clasificacion", sa.String(128), nullable=False),
        sa.Column("referencia_indice", sa.String(128), nullable=False),
        sa.Column("inicio_cobertura", sa.Date(), nullable=False),
        sa.Column("verificado_en", sa.Date(), nullable=False),
        sa.CheckConstraint("frecuencia = 'mensual'", name="frecuencia_mensual"),
        sa.ForeignKeyConstraint(
            ["geografia_id"], ["geografias.id"], name="fk_series_geografia_id_geografias"
        ),
        sa.ForeignKeyConstraint(["rubro_id"], ["rubros.id"], name="fk_series_rubro_id_rubros"),
        sa.PrimaryKeyConstraint("id", name="pk_series"),
        sa.UniqueConstraint("geografia_id", "rubro_id", name="serie_geografia_rubro"),
        sa.UniqueConstraint("id_serie_inegi", name="uq_series_id_serie_inegi"),
    )
    op.create_index("ix_series_geografia_rubro", "series", ["geografia_id", "rubro_id"])
    op.create_table(
        "ejecuciones_etl",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("modo", sa.String(16), nullable=False),
        sa.Column("iniciada_en", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finalizada_en", sa.DateTime(timezone=True)),
        sa.Column("estado", sa.String(16), nullable=False),
        sa.Column("version_catalogo", sa.String(128), nullable=False),
        sa.Column("series_esperadas", sa.Integer(), server_default="792", nullable=False),
        sa.Column("series_recibidas", sa.Integer(), server_default="0", nullable=False),
        sa.Column("observaciones_recibidas", sa.Integer(), server_default="0", nullable=False),
        sa.Column("error_sanitizado", sa.Text()),
        sa.CheckConstraint("modo IN ('bootstrap', 'refresh', 'reconcile')", name="modo_valido"),
        sa.CheckConstraint("estado IN ('iniciada', 'exitosa', 'fallida')", name="estado_valido"),
        sa.CheckConstraint("series_esperadas >= 0", name="series_esperadas_no_negativas"),
        sa.CheckConstraint("series_recibidas >= 0", name="series_recibidas_no_negativas"),
        sa.CheckConstraint("observaciones_recibidas >= 0", name="observaciones_no_negativas"),
        sa.PrimaryKeyConstraint("id", name="pk_ejecuciones_etl"),
    )
    op.create_index(
        "ix_ejecuciones_etl_estado_iniciada", "ejecuciones_etl", ["estado", "iniciada_en"]
    )
    op.create_table(
        "archivos_fuente",
        sa.Column("id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("ejecucion_id", sa.Uuid(), nullable=False),
        sa.Column("geografia_id", sa.String(32), nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("ruta_relativa", sa.Text(), nullable=False),
        sa.Column("parametros", sa.JSON(), server_default=sa.text("'{}'"), nullable=False),
        sa.Column("cobertura_desde", sa.Date()),
        sa.Column("cobertura_hasta", sa.Date()),
        sa.CheckConstraint("char_length(sha256) = 64", name="sha256_longitud"),
        sa.CheckConstraint(
            "cobertura_hasta IS NULL OR cobertura_desde IS NULL OR cobertura_hasta >= cobertura_desde",
            name="cobertura_ordenada",
        ),
        sa.ForeignKeyConstraint(
            ["ejecucion_id"],
            ["ejecuciones_etl.id"],
            name="fk_archivos_fuente_ejecucion_id_ejecuciones_etl",
        ),
        sa.ForeignKeyConstraint(
            ["geografia_id"], ["geografias.id"], name="fk_archivos_fuente_geografia_id_geografias"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_archivos_fuente"),
        sa.UniqueConstraint("ejecucion_id", "geografia_id", name="archivo_ejecucion_geografia"),
    )
    op.create_index("ix_archivos_fuente_ejecucion", "archivos_fuente", ["ejecucion_id"])
    op.create_table(
        "observaciones",
        sa.Column("serie_id", sa.BigInteger(), nullable=False),
        sa.Column("periodo", sa.Date(), nullable=False),
        sa.Column("valor", sa.Numeric(18, 6)),
        sa.Column("archivo_fuente_id", sa.BigInteger(), nullable=False),
        sa.Column("ejecucion_id", sa.Uuid(), nullable=False),
        sa.CheckConstraint("EXTRACT(DAY FROM periodo) = 1", name="periodo_primer_dia"),
        sa.CheckConstraint("valor IS NULL OR valor > 0", name="valor_positivo"),
        sa.ForeignKeyConstraint(
            ["serie_id"], ["series.id"], name="fk_observaciones_serie_id_series"
        ),
        sa.ForeignKeyConstraint(
            ["archivo_fuente_id"],
            ["archivos_fuente.id"],
            name="fk_observaciones_archivo_fuente_id_archivos_fuente",
        ),
        sa.ForeignKeyConstraint(
            ["ejecucion_id"],
            ["ejecuciones_etl.id"],
            name="fk_observaciones_ejecucion_id_ejecuciones_etl",
        ),
        sa.PrimaryKeyConstraint("serie_id", "periodo", name="pk_observaciones"),
    )
    op.create_index("ix_observaciones_periodo_serie", "observaciones", ["periodo", "serie_id"])
    op.create_table(
        "revisiones_observacion",
        sa.Column("id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("serie_id", sa.BigInteger(), nullable=False),
        sa.Column("periodo", sa.Date(), nullable=False),
        sa.Column("valor_anterior", sa.Numeric(18, 6)),
        sa.Column("valor_nuevo", sa.Numeric(18, 6)),
        sa.Column("ejecucion_id", sa.Uuid(), nullable=False),
        sa.Column("archivo_fuente_id", sa.BigInteger(), nullable=False),
        sa.Column("registrada_en", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("EXTRACT(DAY FROM periodo) = 1", name="periodo_primer_dia"),
        sa.CheckConstraint("valor_anterior IS DISTINCT FROM valor_nuevo", name="cambio_real"),
        sa.ForeignKeyConstraint(
            ["serie_id", "periodo"],
            ["observaciones.serie_id", "observaciones.periodo"],
            name="revision_observacion",
        ),
        sa.ForeignKeyConstraint(
            ["ejecucion_id"],
            ["ejecuciones_etl.id"],
            name="fk_revisiones_observacion_ejecucion_id_ejecuciones_etl",
        ),
        sa.ForeignKeyConstraint(
            ["archivo_fuente_id"],
            ["archivos_fuente.id"],
            name="fk_revisiones_observacion_archivo_fuente_id_archivos_fuente",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_revisiones_observacion"),
    )
    op.create_index(
        "ix_revisiones_observacion_serie_periodo",
        "revisiones_observacion",
        ["serie_id", "periodo"],
    )


def downgrade() -> None:
    """Elimina el esquema en orden seguro para la reversión de desarrollo."""
    op.drop_index("ix_revisiones_observacion_serie_periodo", table_name="revisiones_observacion")
    op.drop_table("revisiones_observacion")
    op.drop_index("ix_observaciones_periodo_serie", table_name="observaciones")
    op.drop_table("observaciones")
    op.drop_index("ix_archivos_fuente_ejecucion", table_name="archivos_fuente")
    op.drop_table("archivos_fuente")
    op.drop_index("ix_ejecuciones_etl_estado_iniciada", table_name="ejecuciones_etl")
    op.drop_table("ejecuciones_etl")
    op.drop_index("ix_series_geografia_rubro", table_name="series")
    op.drop_table("series")
    op.drop_table("rubros")
    op.drop_table("geografias")
