"""Definición SQLAlchemy Core del contrato de persistencia."""

from __future__ import annotations

from sqlalchemy import (
    JSON,
    BigInteger,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Identity,
    Index,
    Integer,
    MetaData,
    Numeric,
    String,
    Table,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy import Uuid as UUID

metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "pk": "pk_%(table_name)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

geografias = Table(
    "geografias",
    metadata,
    # The identifiers are stable public IDs from the catalog, not surrogates.
    Column("id", String(32), primary_key=True),
    Column("nivel", String(16), nullable=False),
    Column("nombre", String(200), nullable=False),
    Column("codigo_fuente", String(64), nullable=False, unique=True),
    Column("entidad", String(32)),
    Column("url_fuente", Text, nullable=False),
    CheckConstraint("nivel IN ('nacional', 'entidad', 'ciudad')", name="nivel_valido"),
)

rubros = Table(
    "rubros",
    metadata,
    Column("id", String(64), primary_key=True),
    Column("etiqueta_fuente", String(200), nullable=False),
    Column("orden", Integer, nullable=False, unique=True),
    CheckConstraint("orden > 0", name="orden_positivo"),
)

series = Table(
    "series",
    metadata,
    Column("id", BigInteger, Identity(), primary_key=True),
    Column("geografia_id", String(32), ForeignKey("geografias.id"), nullable=False),
    Column("rubro_id", String(64), ForeignKey("rubros.id"), nullable=False),
    Column("id_serie_inegi", String(32), nullable=False, unique=True),
    Column("etiqueta_fuente", String(300), nullable=False),
    Column("frecuencia", String(16), nullable=False),
    Column("clasificacion", String(128), nullable=False),
    Column("referencia_indice", String(128), nullable=False),
    Column("inicio_cobertura", Date, nullable=False),
    Column("verificado_en", Date, nullable=False),
    UniqueConstraint("geografia_id", "rubro_id", name="serie_geografia_rubro"),
    CheckConstraint("frecuencia = 'mensual'", name="frecuencia_mensual"),
)

ejecuciones_etl = Table(
    "ejecuciones_etl",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("modo", String(16), nullable=False),
    Column("iniciada_en", DateTime(timezone=True), nullable=False),
    Column("finalizada_en", DateTime(timezone=True)),
    Column("estado", String(16), nullable=False),
    Column("version_catalogo", String(128), nullable=False),
    Column("series_esperadas", Integer, nullable=False, server_default="792"),
    Column("series_recibidas", Integer, nullable=False, server_default="0"),
    Column("observaciones_recibidas", Integer, nullable=False, server_default="0"),
    Column("error_sanitizado", Text),
    CheckConstraint("modo IN ('bootstrap', 'refresh', 'reconcile')", name="modo_valido"),
    CheckConstraint("estado IN ('iniciada', 'exitosa', 'fallida')", name="estado_valido"),
    CheckConstraint("series_esperadas >= 0", name="series_esperadas_no_negativas"),
    CheckConstraint("series_recibidas >= 0", name="series_recibidas_no_negativas"),
    CheckConstraint("observaciones_recibidas >= 0", name="observaciones_no_negativas"),
)

archivos_fuente = Table(
    "archivos_fuente",
    metadata,
    Column("id", BigInteger, Identity(), primary_key=True),
    Column("ejecucion_id", UUID(as_uuid=True), ForeignKey("ejecuciones_etl.id"), nullable=False),
    Column("geografia_id", String(32), ForeignKey("geografias.id"), nullable=False),
    Column("sha256", String(64), nullable=False),
    Column("ruta_relativa", Text, nullable=False),
    Column("parametros", JSON, nullable=False, server_default=text("'{}'")),
    Column("cobertura_desde", Date),
    Column("cobertura_hasta", Date),
    UniqueConstraint("ejecucion_id", "geografia_id", name="archivo_ejecucion_geografia"),
    CheckConstraint("char_length(sha256) = 64", name="sha256_longitud"),
    CheckConstraint(
        "cobertura_hasta IS NULL OR cobertura_desde IS NULL OR cobertura_hasta >= cobertura_desde",
        name="cobertura_ordenada",
    ),
)

observaciones = Table(
    "observaciones",
    metadata,
    Column("serie_id", BigInteger, ForeignKey("series.id"), primary_key=True),
    Column("periodo", Date, primary_key=True),
    Column("valor", Numeric(18, 12)),
    Column("archivo_fuente_id", BigInteger, ForeignKey("archivos_fuente.id"), nullable=False),
    Column("ejecucion_id", UUID(as_uuid=True), ForeignKey("ejecuciones_etl.id"), nullable=False),
    CheckConstraint("EXTRACT(DAY FROM periodo) = 1", name="periodo_primer_dia"),
    CheckConstraint("valor IS NULL OR valor > 0", name="valor_positivo"),
)

revisiones_observacion = Table(
    "revisiones_observacion",
    metadata,
    Column("id", BigInteger, Identity(), primary_key=True),
    Column("serie_id", BigInteger, nullable=False),
    Column("periodo", Date, nullable=False),
    Column("valor_anterior", Numeric(18, 12)),
    Column("valor_nuevo", Numeric(18, 12)),
    Column("ejecucion_id", UUID(as_uuid=True), ForeignKey("ejecuciones_etl.id"), nullable=False),
    Column("archivo_fuente_id", BigInteger, ForeignKey("archivos_fuente.id"), nullable=False),
    Column("registrada_en", DateTime(timezone=True), nullable=False),
    ForeignKeyConstraint(
        ["serie_id", "periodo"],
        ["observaciones.serie_id", "observaciones.periodo"],
        name="revision_observacion",
    ),
    CheckConstraint("EXTRACT(DAY FROM periodo) = 1", name="periodo_primer_dia"),
    CheckConstraint("valor_anterior IS DISTINCT FROM valor_nuevo", name="cambio_real"),
)

Index("ix_series_geografia_rubro", series.c.geografia_id, series.c.rubro_id)
Index("ix_ejecuciones_etl_estado_iniciada", ejecuciones_etl.c.estado, ejecuciones_etl.c.iniciada_en)
Index("ix_archivos_fuente_ejecucion", archivos_fuente.c.ejecucion_id)
Index("ix_observaciones_periodo_serie", observaciones.c.periodo, observaciones.c.serie_id)
Index(
    "ix_revisiones_observacion_serie_periodo",
    revisiones_observacion.c.serie_id,
    revisiones_observacion.c.periodo,
)
