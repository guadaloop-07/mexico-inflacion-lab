"""Conexiones PostgreSQL creadas solamente cuando un consumidor las solicita."""

from __future__ import annotations

from urllib.parse import unquote, urlsplit

from sqlalchemy import Engine
from sqlalchemy import create_engine as sqlalchemy_create_engine

from inflacion_lab.config import ConfigurationError


def create_engine(database_url: str) -> Engine:
    """Crea un motor síncrono para una URL PostgreSQL ya configurada."""
    return sqlalchemy_create_engine(database_url, pool_pre_ping=True)


def require_test_database_url(database_url: str | None) -> str:
    """Acepta solo una base dedicada de pruebas antes de cualquier operación."""
    if not database_url:
        raise ConfigurationError("Falta TEST_DATABASE_URL para ejecutar pruebas de integración.")
    parsed = urlsplit(database_url)
    database_name = unquote(parsed.path.lstrip("/"))
    if (
        not parsed.scheme.startswith(("postgres", "postgresql"))
        or not parsed.netloc
        or not database_name
        or "/" in database_name
        or not database_name.endswith("_test")
    ):
        raise ConfigurationError(
            "TEST_DATABASE_URL debe identificar una base cuyo nombre termine en '_test'."
        )
    return database_url
