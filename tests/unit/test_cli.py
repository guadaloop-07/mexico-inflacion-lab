from __future__ import annotations

import importlib

import pytest

from inflacion_lab.cli import main


def test_imports_do_not_require_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    for variable in (
        "DATABASE_URL_MIGRATIONS",
        "DATABASE_URL_ETL",
        "DATABASE_URL_API",
        "TEST_DATABASE_URL",
    ):
        monkeypatch.delenv(variable, raising=False)

    package = importlib.import_module("inflacion_lab")
    importlib.import_module("inflacion_lab.cli")
    importlib.import_module("inflacion_lab.config")

    assert package.__version__ == "0.1.0"


def test_help_is_available_without_configuration(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exit_status:
        main(["--help"])

    assert exit_status.value.code == 0
    assert "Herramientas para preparar" in capsys.readouterr().out


def test_version_is_available_without_configuration(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exit_status:
        main(["--version"])

    assert exit_status.value.code == 0
    assert "inflacion-lab 0.1.0" in capsys.readouterr().out
