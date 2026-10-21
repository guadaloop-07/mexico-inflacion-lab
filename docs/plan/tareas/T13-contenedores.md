# T13 · Empaquetado y roles para servidor

Dependencias: T10, T11, T12. Rama sugerida: `feat/t13-contenedores`.

## Objetivo

Construir la aplicación desde un clon limpio y ejecutarla como servicios
reproducibles, preparada para el proxy y servidor que se acuerden en T16.

## Leer

`AGENTS.md`, `../ejecucion.md`, `../arquitectura.md`, `../operacion.md` y rutas de
`../api.md`.

## Implementar

- Dockerfiles con etapas de build/runtime; API y ETL comparten imagen. Instalar
  dependencias con lockfiles y compilar web con Node 24/npm ci.
- Compose para producción y comando puntual de migración; servicios DB/API/web,
  job ETL y volúmenes persistentes con permisos correctos.
- Roles separados de migración, ETL y lectura API; provisionar contraseñas por
  entorno, sin escribir secretos en archivos versionados o argumentos visibles.
- Healthchecks y arranque ordenado, usuario de aplicación sin privilegios y
  configuración sanitizada. Sin puerto Postgres público en producción.
- Configuración de rutas para el proxy con base `/inflacion/` y
  `/api/inflacion/v1`; documentar alternativa si el dominio final cambia.
- Ensayo local desde imágenes, con base de verificación separada.

## Aceptación y comprobación

- Build desde un clon limpio sin depender de node_modules/.venv del host.
- Persistencia después de recrear servicios; defaults y secretos distinguidos.
- La API consulta y no puede INSERT/UPDATE/DELETE en observaciones con su rol.
- Migraciones se ejecutan antes de servir; no desde cada worker concurrente.
- Assets y API funcionan bajo los prefijos previstos, incluyendo errores 404
  de API que no se convierten en HTML. La web no llama a localhost en producción.
- Reinicio de servicios sin perder datos ni publicar un lote incompleto.
- `make check`, suites existentes y ensayo Compose pasan; registrar resultado
  en `docs/evidencias/T13.md`.

Esta tarea prepara y prueba contenedores; no constituye un despliegue externo.
