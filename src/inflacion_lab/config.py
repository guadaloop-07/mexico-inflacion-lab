"""Configuración tipada y diferida para los componentes de la aplicación."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

DatabaseRole = Literal["migrations", "etl", "api", "test"]


class ConfigurationError(ValueError):
    """Indica un valor ausente o inválido de configuración."""


@dataclass(frozen=True)
class Settings:
    """Valores de entorno sin inicializar conexiones al importarlos."""

    database_url_migrations: str | None
    database_url_etl: str | None
    database_url_api: str | None
    test_database_url: str | None
    inpc_export_url: str | None
    data_dir: Path
    catalog_path: Path
    refresh_months: int
    api_prefix: str
    web_base_path: str

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> Settings:
        """Lee valores de entorno sin exigir secretos que aún no se usan."""
        values = os.environ if environ is None else environ
        refresh_months = _positive_integer(values.get("REFRESH_MONTHS", "24"), "REFRESH_MONTHS")
        return cls(
            database_url_migrations=_optional(values.get("DATABASE_URL_MIGRATIONS")),
            database_url_etl=_optional(values.get("DATABASE_URL_ETL")),
            database_url_api=_optional(values.get("DATABASE_URL_API")),
            test_database_url=_optional(values.get("TEST_DATABASE_URL")),
            inpc_export_url=_optional(values.get("INPC_EXPORT_URL")),
            data_dir=Path(values.get("DATA_DIR", "data")),
            catalog_path=Path(values.get("CATALOG_PATH", "config/series.yml")),
            refresh_months=refresh_months,
            api_prefix=_path_prefix(values.get("API_PREFIX", "/api/inflacion/v1"), "API_PREFIX"),
            web_base_path=_path_prefix(values.get("WEB_BASE_PATH", "/inflacion/"), "WEB_BASE_PATH"),
        )

    def database_url(self, role: DatabaseRole) -> str:
        """Devuelve y valida la URL solo cuando el componente la necesita."""
        variable, value = {
            "migrations": ("DATABASE_URL_MIGRATIONS", self.database_url_migrations),
            "etl": ("DATABASE_URL_ETL", self.database_url_etl),
            "api": ("DATABASE_URL_API", self.database_url_api),
            "test": ("TEST_DATABASE_URL", self.test_database_url),
        }[role]
        if value is None:
            raise ConfigurationError(f"Falta {variable}; defínela antes de usar la base de datos.")
        _validate_database_url(value, variable)
        return value


def _optional(value: str | None) -> str | None:
    return value.strip() if value and value.strip() else None


def _positive_integer(value: str, variable: str) -> int:
    try:
        parsed = int(value)
    except ValueError as error:
        raise ConfigurationError(f"{variable} debe ser un entero positivo.") from error
    if parsed <= 0:
        raise ConfigurationError(f"{variable} debe ser un entero positivo.")
    return parsed


def _path_prefix(value: str, variable: str) -> str:
    if not value.startswith("/"):
        raise ConfigurationError(f"{variable} debe iniciar con '/'.")
    return value


def _validate_database_url(value: str, variable: str) -> None:
    parsed = urlsplit(value)
    if (
        not parsed.scheme.startswith(("postgres", "postgresql"))
        or not parsed.netloc
        or not parsed.path
    ):
        raise ConfigurationError(f"{variable} debe ser una URL válida de PostgreSQL.")
