"""Punto de entrada para ``python -m inflacion_lab``."""

from .cli import main

if __name__ == "__main__":  # pragma: no cover - lo ejecuta el intérprete.
    raise SystemExit(main())
