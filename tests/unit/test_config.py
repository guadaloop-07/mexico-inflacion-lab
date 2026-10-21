from __future__ import annotations

import pytest

from inflacion_lab.config import ConfigurationError, Settings


def test_settings_do_not_require_secrets_to_load() -> None:
    settings = Settings.from_env({})

    assert settings.data_dir.name == "data"
    assert settings.refresh_months == 24


def test_missing_database_url_fails_only_when_it_is_used() -> None:
    settings = Settings.from_env({})

    with pytest.raises(ConfigurationError, match="DATABASE_URL_API"):
        settings.database_url("api")


def test_invalid_database_url_has_a_readable_error() -> None:
    settings = Settings.from_env({"DATABASE_URL_API": "no-es-una-url"})

    with pytest.raises(ConfigurationError, match="DATABASE_URL_API debe ser una URL válida"):
        settings.database_url("api")


def test_database_url_is_accepted_when_the_component_uses_it() -> None:
    expected = "postgresql+psycopg://usuario:secreto@localhost:5432/inflacion_lab"
    settings = Settings.from_env({"DATABASE_URL_API": expected})

    assert settings.database_url("api") == expected
