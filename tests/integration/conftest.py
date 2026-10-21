"""Aislamiento explícito de la base utilizada en pruebas de integración."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from alembic.config import Config
from sqlalchemy import Engine

from alembic import command
from inflacion_lab.db.conexion import create_engine, require_test_database_url


@pytest.fixture(scope="session")
def test_database_url() -> str:
    """Valida el destino antes de que cualquier fixture pueda ejecutar DDL."""
    return require_test_database_url(os.environ.get("TEST_DATABASE_URL"))


@pytest.fixture(scope="session")
def migrated_engine(test_database_url: str) -> Engine:
    """Aplica la migración inicial de forma idempotente en la base aislada."""
    os.environ["DATABASE_URL_MIGRATIONS"] = test_database_url
    config = Config(str(Path("alembic.ini")))
    command.upgrade(config, "head")
    return create_engine(test_database_url)
