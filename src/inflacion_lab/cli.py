"""Interfaz de línea de comandos del laboratorio."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from . import __version__
from .catalogo import CatalogError, load_catalog
from .etl.ejecucion import FetchRunError, fetch_catalog


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

    etl = subcommands.add_parser("etl", help="descarga y prepara originales del INPC")
    etl_subcommands = etl.add_subparsers(dest="etl_command")
    fetch = etl_subcommands.add_parser("fetch", help="descarga y valida el catálogo completo")
    fetch.add_argument("--ruta", type=Path, default=Path("config/series.yml"))
    fetch.add_argument("--data-dir", type=Path, default=Path("data"))
    fetch.add_argument("--inicio", type=int, default=2018)
    fetch.add_argument("--fin", type=int)
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
    if namespace.command == "etl" and namespace.etl_command == "fetch":
        try:
            catalogo = load_catalog(namespace.ruta)
            result = fetch_catalog(
                catalogo,
                data_dir=namespace.data_dir,
                start_year=namespace.inicio,
                end_year=namespace.fin,
            )
        except (CatalogError, FetchRunError, ValueError) as error:
            parser.error(str(error))
        print(
            f"Extracción válida: {result.geografias_ok}/{len(catalogo.geografias)} "
            f"geografías, {result.series_recibidas}/{catalogo.total_series} series, "
            f"{result.observaciones} observaciones. Originales: {result.run_dir}."
        )
    return 0
