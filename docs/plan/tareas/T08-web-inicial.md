# T08 · Primera vista nacional y base frontend

Dependencias: T07. Rama sugerida: `feat/t08-web-inicial`.

## Objetivo

Cumplir D2: ver tasas y trayectoria de México en una página alimentada por la
API real, sobre la carga completa de las 792 series.

## Leer

`AGENTS.md`, `../ejecucion.md`, `../interfaz.md`, `../api.md`,
`../arquitectura.md` y validación frontend de `../validacion.md`.

## Implementar

- `web/` con React/TypeScript/Vite, Node 24, npm y lockfile. Añadir los archivos
  generados locales a `.gitignore` donde corresponda.
- Cliente de API y tipos compartidos dentro de web. Proxy de desarrollo y base
  `/inflacion/` configurable; sin URLs de localhost incrustadas en producción.
- Resumen anual/mensual nacional, periodo visible e historia con ECharts.
- Controles iniciales de mensual/anual, mes de corte e inicio de historia.
  Nivel del índice como exploración adicional con referencia explicada.
- Estados de carga/vacío/error/nulos y fuente. No usar fixtures como fallback.
- CSS variables y estructura responsiva. Tabla accesible de la gráfica.
- ESLint, formato y TypeScript; Vitest/Testing Library. Hooks web ejecutados al
  cambiar archivos web, con `pass_filenames: false` si npm corre desde `web/`.
- `make setup-web`, `make web`, `make test-web`, `make build-web`. Preparar Node
  antes de `make check` en CI, añadir `npm ci`, tipos, tests y build obligatorios.

## Aceptación y comprobación

- Una carga completa local produce una gráfica real y un resumen concordante.
- Tests de componentes usan respuestas rotuladas de prueba, verifican cambio de
  medida y estados; TypeScript no sustituye esas pruebas de comportamiento.
- Las respuestas antiguas no sobrescriben una selección más reciente. Se trata
  el cambio de versión de datos sin mezclar indefinidamente componentes.
- Navegación por teclado y visualización comprobadas en 360 y 1280 px.
- `make check`, suites Python/DB, `make test-web`, `make build-web` y CI pasan.
- Documentar en `docs/evidencias/T08.md` la conexión real y la inspección visual.

Todavía no implementar las vistas de comparación/rubros ni calculadora. La web
inicial no limita ni modifica la cobertura del ETL existente.
