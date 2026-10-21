"""Interfaz de línea de comandos del laboratorio."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from . import __version__


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
    return parser


def main(args: Sequence[str] | None = None) -> int:
    """Ejecuta la CLI base y devuelve un código de salida exitoso."""
    build_parser().parse_args(args)
    return 0
