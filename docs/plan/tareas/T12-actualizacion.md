# T12 · Actualización programable y frescura

Dependencias: T05, T09. Rama sugerida: `feat/t12-actualizacion`.

## Objetivo

Hacer repetible la actualización de las 792 series y distinguir el éxito del
proceso de la existencia de nuevos periodos de datos.

## Leer

`AGENTS.md`, `../ejecucion.md`, `../operacion.md`, actualizaciones de
`../datos.md` y metadatos de `../api.md`.

## Implementar

- `etl status` con último intento, última carga válida y periodo por serie/nivel.
- Resumen de frescura para el usuario y logs estructurados sanitizados.
- Calendario oficial verificado del año operativo en configuración con fuente
  y fecha de revisión. Sin calendario, informar esa condición explícitamente.
- Unidades/timers bajo `deploy/`: refresh diario y reconciliación mensual con
  zona horaria explícita, reintentos limitados y bloqueo de escritor existente.
- Documentación de instalación, consulta de logs y ejecución manual. Todavía no
  activar jobs en un servidor no especificado.
- Reflejar en metadatos/UI la diferencia entre descarga reciente y periodo viejo.

## Aceptación y comprobación

- Pruebas con reloj controlado: mismo periodo sin cambios, mes nuevo, fallo,
  calendario ausente/desactualizado y refresh alrededor de un cambio de año.
- Un refresh conserva cobertura de las 792 series y captura correcciones dentro
  de ventana; una reconcile captura una corrección más antigua.
- Un calendario vencido no sigue afirmando frescura con fechas supuestas.
- Una ejecución concurrente informa bloqueo y no publica parcialmente.
- Tests no activan timers reales, llaman al INEGI ni envían notificaciones.
- `make check`, suites pertinentes y CI pasan; documentar el ensayo de comandos.

La elección de canal/destinatario de avisos queda para T16 con la propietaria.
