# T15 · Respaldo y restauración demostrados

Dependencias: T13. Rama sugerida: `feat/t15-respaldos`.

## Objetivo

Demostrar que el estado publicado puede recuperarse junto a sus originales y
configuración, antes de confiar el producto a un servidor público.

## Leer

`AGENTS.md`, `../ejecucion.md`, respaldo/rollback de `../operacion.md`,
publicación de `../datos.md` y aislamiento de `../validacion.md`.

## Implementar

- Comandos versionados para dump custom y respaldo de catálogo/manifiestos/
  originales, con checksum y metadatos de versión.
- Coordinación con el bloqueo ETL para evitar referencias a originales ausentes
  del respaldo. Roles y secretos recuperables según configuración documentada.
- Restauración en base y directorio separados; salvaguardas sobre el destino.
- Configuración de retención y preparación de copia cifrada externa. El destino
  real lo aporta la propietaria; no contratar ni aprovisionar cuentas por defecto.
- Runbook paso a paso, incluyendo quién conserva la clave de recuperación.

## Aceptación y comprobación

- Restaurar una copia local en una base `_test` y directorio separado; comparar
  catálogo, conteos, revisión histórica, tasas y última publicación.
- Comprobar hashes y existencia de originales referenciados por observaciones.
- Rechazar un destino de restauración ambiguo o equivalente al origen.
- Una prueba con respaldo corrupto produce error, sin sustituirlo por un éxito.
- Registrar duración y pérdida de datos estimada frente a los objetivos de
  operación en `docs/evidencias/T15.md`.
- `make check`, pruebas pertinentes y CI pasan. Si falta copia externa, indicarlo
  como requisito pendiente para el lanzamiento de T16.

Nunca probar la restauración borrando la base de producción. Un dump creado sin
una restauración verificada no satisface esta tarea.
