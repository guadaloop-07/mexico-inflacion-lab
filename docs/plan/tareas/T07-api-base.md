# T07 · API de lectura para catálogo, resumen e historia

Dependencias: T06. Rama sugerida: `feat/t07-api-base`.

## Objetivo

Exponer el catálogo completo y las primeras consultas, listas para una web real.
El backend acepta todas las geografías aunque T08 muestre primero México.

## Leer

`AGENTS.md`, `../ejecucion.md`, `../arquitectura.md`, `../api.md` y
`../validacion.md`.

## Implementar

- FastAPI, Pydantic 2 y Uvicorn; fábrica de aplicación y conexiones configuradas
  para lectura. Sin consulta al INEGI durante peticiones.
- `/catalogo`, `/resumen`, `/series`, `/health/live` y `/health/ready`, bajo el
  prefijo acordado. `make api` y documentación OpenAPI.
- Parámetros tipados, límites, motivos de nulos, sobre y errores del contrato.
- Lectura `REPEATABLE READ` de valores/versiones dentro de una respuesta; caché corta,
  ETag y respuesta 304 cuando corresponda.
- Última publicación, periodo de fuente y vacío previo a la primera carga como
  estados diferenciados. No exigir credenciales al importar la aplicación.

## Aceptación y comprobación

- Tests de endpoints contra Postgres aislado, usando dependencia de conexión de
  prueba; no conexiones a producción ni llamadas de red al INEGI.
- La respuesta nacional y otra ubicación reproducen la consulta canónica.
- Fechas invertidas, selección desconocida y rango excesivo generan el error
  del contrato. Nulos y ausencia de una publicación tienen estados explícitos.
- Healthcheck no imprime credenciales. Readiness detecta esquema no disponible.
- ETag cambia con parámetros/versión y devuelve 304 para el contenido vigente.
- `make check`, `make test`, `make test-db` y CI pasan.

No agregar endpoints de escritura, un login ni un proceso ETL embebido en API.
