# T01 · Paquete Python y verificación básica

Dependencias: base de Git integrada. Rama sugerida: `feat/t01-base-python`.

## Objetivo

Dejar una aplicación Python instalable, configurable y comprobable sin descargar
datos ni conectar a Postgres. Es la base de las tareas siguientes.

## Leer

`AGENTS.md`, `../ejecucion.md`, `../arquitectura.md` y `../validacion.md`.

## Implementar

- Paquete `src/inflacion_lab`, backend de construcción y entrada `inflacion-lab`.
  Ajustar `pyproject.toml` y `uv.lock`; retirar `tool.uv.package = false`.
- CLI con ayuda y versión, también mediante `python -m inflacion_lab`.
- Configuración tipada y `.env.example` con nombres y valores ficticios. La
  importación y ayuda no exigen base ni secretos; validar cada URL al usarla.
- pytest y estructura `tests/unit`, marca `integration` y `make test`.
- Agregar tests unitarios al check `Calidad`, conservando los hooks y protección.
- Documentar los comandos que realmente queden disponibles.

## Aceptación y comprobación

- `uv sync --locked`, `uv run inflacion-lab --help` y
  `uv run python -m inflacion_lab --help` funcionan en un entorno nuevo.
- `make check` y `make test` pasan sin red, Docker ni credenciales.
- Tests cubren configuración inválida con error legible y ausencia de secretos
  al consultar ayuda/importar. Ningún import inicia procesos o conexiones.
- CI ejecuta tests reales y no omite fallos.

No crear todavía ETL, API ni directorios frontend vacíos. Registrar el PR y
resultado de CI en `../seguimiento.md` según el procedimiento de ejecución.
