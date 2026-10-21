"""Interfaz de línea de comandos del laboratorio."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from . import __version__
from .catalogo import CatalogError, load_catalog
from .config import ConfigurationError, Settings


def build_parser() -> argparse.ArgumentParser:
    """Construye el parser sin leer configuración ni abrir conexiones."""
    parser = argparse.ArgumentParser(
        prog="inflacion-lab",
        description="Herramientas para preparar y explorar datos del INPC.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="muestra la versión instalada y termina",
    )
    subcommands = parser.add_subparsers(dest="command")
    catalogo = subcommands.add_parser("catalogo", help="opera el catálogo de series del INPC")
    catalogo_subcommands = catalogo.add_subparsers(dest="catalog_command")
    validar = catalogo_subcommands.add_parser(
        "validar", help="valida el catálogo sin acceder a la red"
    )
    validar.add_argument("--ruta", type=Path, default=Path("config/series.yml"))
    registrar = catalogo_subcommands.add_parser(
        "registrar", help="registra el catálogo completo en PostgreSQL"
    )
    registrar.add_argument("--ruta", type=Path, default=Path("config/series.yml"))
    return parser


def main(args: Sequence[str] | None = None) -> int:
    """Ejecuta la CLI base y devuelve un código de salida exitoso."""
    parser = build_parser()
    namespace = parser.parse_args(args)
    if namespace.command == "catalogo" and namespace.catalog_command == "validar":
        try:
            catalogo = load_catalog(namespace.ruta)
        except CatalogError as error:
            parser.error(str(error))
        print(
            f"Catálogo válido: {len(catalogo.geografias)} geografías, "
            f"{len(catalogo.rubros)} rubros y {catalogo.total_series} series."
        )
    if namespace.command == "catalogo" and namespace.catalog_command == "registrar":
        try:
            catalogo = load_catalog(namespace.ruta)
            from .db.catalogo import register_catalog
            from .db.conexion import create_engine

            with create_engine(
                Settings.from_env().database_url("migrations")
            ).begin() as connection:
                register_catalog(connection, catalogo)
        except (CatalogError, ConfigurationError, ValueError) as error:
            parser.error(str(error))
        print(
            f"Catálogo registrado: {len(catalogo.geografias)} geografías, "
            f"{len(catalogo.rubros)} rubros y {catalogo.total_series} series."
        )
    return 0
