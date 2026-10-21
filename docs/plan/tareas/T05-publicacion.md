# T05 · Primera carga completa y publicación transaccional

Dependencias: T03, T04. Rama sugerida: `feat/t05-publicacion-completa`.

## Objetivo

Cumplir D1: primera carga real desde 2018 con las **792 series**, recuperación
ante fallo y evidencia de idempotencia. No hay publicación parcial de producto.

## Leer

`AGENTS.md`, `../ejecucion.md`, `../datos.md`, `../validacion.md` y resultados
integrados de T02–T04.

## Implementar

- `etl/validacion.py`: informe por serie y cobertura completa del catálogo.
- `etl/ejecucion.py`: bloqueo de escritor, registro de ejecución, transporte y
  validación fuera de la transacción final; preparación de tabla temporal.
- `db/carga.py`: upsert de observaciones, auditoría de valores cambiados y estado
  exitoso en una sola transacción, incluyendo cambios del catálogo publicado.
  Nulos legítimos y origen preservados.
- Al fallar cualquier parte, mantener observaciones/revisiones anteriores y
  registrar el error por separado; liberar bloqueo y salir distinto de cero.
- `etl run --mode bootstrap|refresh|reconcile`, siempre para 792 series, y los
  targets `make etl-bootstrap`, `make etl-refresh`, `make etl-reconcile`.
- Ventana reciente de 24 meses y reconciliación completa según datos.md.
  `refresh` exige un bootstrap completo previo; no crea una historia inicial
  truncada. `reconcile` obtiene toda la historia desde 2018.
- Primera ejecución real completa y reporte `docs/evidencias/T05.md` sin archivos
  originales completos ni credenciales en Git.

## Aceptación y comprobación

- Las 88 ubicaciones y 792 series quedan verificadas/cargadas en el bootstrap.
  Explicar nulos legítimos y rangos distintos, sin exigir valores inventados.
- Repetir un lote idéntico no agrega observaciones ni revisiones de valores.
- Corregir un valor lo actualiza y conserva anterior/nuevo/origen en auditoría.
- Una serie faltante o un fallo al final revierte toda la publicación. En tests,
  verificar que la versión anterior sigue siendo la visible.
- Dos escritores no publican simultáneamente; el bloqueo se libera tras fallo.
- La ejecución conserva originales y conteos suficientes para reproducirla.
- `make check`, `make test`, `make test-db` y CI pasan; contrastar los conteos
  del reporte con consultas independientes.

Si la fuente o el entorno impiden el bootstrap real, dejar preparada y probada
la carga, pero registrar D1 pendiente y la causa concreta. Una prueba con tres
geografías no satisface la cobertura real exigida por esta tarea.
