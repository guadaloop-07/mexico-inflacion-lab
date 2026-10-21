"""Registro repetible del catálogo validado en PostgreSQL."""

from __future__ import annotations

from datetime import date

from sqlalchemy import Connection
from sqlalchemy.dialects.postgresql import insert

from inflacion_lab.catalogo import Catalogo
from inflacion_lab.db.tablas import geografias, rubros, series


def register_catalog(connection: Connection, catalog: Catalogo) -> None:
    """Inserta o actualiza las identidades del catálogo sin crear duplicados."""
    for rubro in catalog.rubros:
        values = {
            "id": rubro.id,
            "etiqueta_fuente": rubro.etiqueta_fuente,
            "orden": rubro.orden,
        }
        statement = insert(rubros).values(values)
        connection.execute(
            statement.on_conflict_do_update(
                index_elements=[rubros.c.id],
                set_={key: statement.excluded[key] for key in values if key != "id"},
            )
        )

    for geografia in catalog.geografias:
        geography_values = {
            "id": geografia.id,
            "nivel": geografia.nivel,
            "nombre": geografia.nombre,
            "codigo_fuente": geografia.id_estructura,
            "entidad": geografia.entidad,
            "url_fuente": geografia.url_fuente,
        }
        geography_statement = insert(geografias).values(geography_values)
        connection.execute(
            geography_statement.on_conflict_do_update(
                index_elements=[geografias.c.id],
                set_={
                    key: geography_statement.excluded[key]
                    for key in geography_values
                    if key != "id"
                },
            )
        )
        for serie in geografia.series:
            series_values = {
                "geografia_id": geografia.id,
                "rubro_id": serie.rubro_id,
                "id_serie_inegi": serie.id_serie_inegi,
                "etiqueta_fuente": serie.etiqueta_fuente,
                "frecuencia": serie.frecuencia,
                "clasificacion": serie.clasificacion,
                "referencia_indice": serie.referencia_indice,
                "inicio_cobertura": _month_start(serie.inicio_cobertura),
                "verificado_en": date.fromisoformat(serie.verificado_en),
            }
            series_statement = insert(series).values(series_values)
            connection.execute(
                series_statement.on_conflict_do_update(
                    index_elements=[series.c.geografia_id, series.c.rubro_id],
                    set_={
                        key: series_statement.excluded[key]
                        for key in series_values
                        if key not in {"geografia_id", "rubro_id"}
                    },
                )
            )


def _month_start(value: str) -> date:
    """Convierte el mes de cobertura del catálogo a su primer día."""
    return date.fromisoformat(f"{value}-01")
