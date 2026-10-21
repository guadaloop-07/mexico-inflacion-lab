# T03 · Postgres y migraciones

Dependencias: T02. Rama sugerida: `feat/t03-postgres`.

## Objetivo

Crear el esquema de siete tablas del contrato, migraciones reproducibles y una
base de pruebas aislada. Todavía no publicar datos del INEGI.

## Leer

`AGENTS.md`, `../ejecucion.md`, `../arquitectura.md`, esquema de `../datos.md`,
y `../validacion.md`.

## Implementar

- Dependencias SQLAlchemy Core 2.1, psycopg 3 y Alembic; actualizar lockfile.
- `db/tablas.py`, fábrica de conexiones y migración inicial de las siete tablas.
- Restricciones de fechas, niveles, claves naturales/FKs e índices útiles para
  consultas de serie-periodo. Índices de precios `NUMERIC(18,6)` nullable.
- Registro del catálogo completo en la base mediante un comando repetible.
- Compose de desarrollo con PostgreSQL 18, healthcheck y volumen correcto para
  esa versión; puerto de desarrollo enlazado a localhost.
- `make db-up`, `make db-migrate` y `make test-db`.
- Fixture de integración que solo opere si `TEST_DATABASE_URL` identifica una
  base terminada en `_test`. No derivar la URL desde producción como fallback.
- Servicio Postgres en CI; unitarias e integración dentro del check `Calidad`.

## Aceptación y comprobación

- Una base vacía alcanza `alembic upgrade head`; repetir no modifica el esquema.
- Persistencia verificada tras recrear el contenedor sin borrar el volumen.
- Integración comprueba restricciones y conservación exacta de decimales/nulos.
- Registrar el catálogo dos veces conserva 88 geografías, nueve rubros y 792
  series, sin duplicados.
- Una URL de pruebas sin el sufijo permitido se rechaza antes de cualquier DDL.
- `make check`, `make test` y `make test-db` pasan. Registrar los comandos de
  preparación de la base `_test` y limitaciones reales del entorno.

La separación de roles de producción se completa en T13. No se necesita todavía
un catálogo geográfico remoto ni un servidor externo de bases de datos.
