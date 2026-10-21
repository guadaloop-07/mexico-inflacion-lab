from __future__ import annotations

import pytest

from inflacion_lab.config import ConfigurationError
from inflacion_lab.db.conexion import require_test_database_url


def test_test_database_url_rejects_a_database_without_the_test_suffix() -> None:
    with pytest.raises(ConfigurationError, match="termine en '_test'"):
        require_test_database_url("postgresql+psycopg://user:secret@localhost/inflacion_lab")


def test_test_database_url_accepts_only_a_dedicated_database() -> None:
    url = "postgresql+psycopg://user:secret@localhost/inflacion_lab_test"

    assert require_test_database_url(url) == url
