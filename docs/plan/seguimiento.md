# Seguimiento

Estado al redactar el plan: solo la base de Git/CI está integrada. Todas las
tareas de aplicación están pendientes. Este documento se actualiza con evidencia
real; una dependencia se considera cumplida después de confirmar su merge.

Estados: `pendiente`, `en curso`, `PR abierto`, `integrada`, `bloqueada`.

| ID | Estado | PR / commit integrado | Evidencia y limitaciones |
|---|---|---|---|
| T01 | integrada | [#3](https://github.com/guadaloop-07/mexico-inflacion-lab/pull/3) / `6a926f8` | Paquete y CLI base; `make test` (7 pruebas) y `make check` pasan localmente. `Calidad` pasó en CI. Integrada el 21 de octubre de 2026. |
| T02 | integrada | [#4](https://github.com/guadaloop-07/mexico-inflacion-lab/pull/4) / `5a75488` | Catálogo de 792 identidades y fixtures oficiales; `Calidad` pasó en CI. Integrada el 21 de octubre de 2026. |
| T03 | integrada | [#5](https://github.com/guadaloop-07/mexico-inflacion-lab/pull/5) / `1ee6bc8` | Esquema PostgreSQL, migración, catálogo repetible y pruebas de integración. `Calidad` pasó en CI. Integrada el 22 de octubre de 2026. |
| T04 | integrada | [#6](https://github.com/guadaloop-07/mexico-inflacion-lab/pull/6) / `59aeaef` | Extracción agrupada, parser y originales atómicos; `Calidad` pasó. Integrada el 22 de octubre de 2026. |
| T05 | integrada | [#7](https://github.com/guadaloop-07/mexico-inflacion-lab/pull/7) / `2160b41` | Carga transaccional probada; `Calidad` pasó. El bootstrap en vivo recibió HTTP 500 para las 88 geografías y D1 sigue pendiente. |
| T06 | integrada | [#8](https://github.com/guadaloop-07/mexico-inflacion-lab/pull/8) / `31a0579` | Vistas canónicas y consultas decimales; `Calidad` pasó. Integrada el 26 de octubre de 2026. |
| T07 | en curso | — | API de catálogo, resumen, historia y salud implementada; falta abrir PR y confirmar CI. |
| T08 | pendiente | — | — |
| T09 | pendiente | — | — |
| T10 | pendiente | — | — |
| T11 | pendiente | — | — |
| T12 | pendiente | — | — |
| T13 | pendiente | — | — |
| T14 | pendiente | — | — |
| T15 | pendiente | — | — |
| T16 | pendiente | — | Faltan datos del servidor, dominio/proxy y destino externo del respaldo |
| T17 | pendiente | — | Requiere una publicación mensual posterior al despliegue |

## Registro de cada entrega

Al abrir un PR añadir una entrada con este formato; confirmar el merge en la
siguiente tarea o cuando la propietaria lo indique:

```text
Txx · fecha
Resultado: comportamiento implementado y criterios de la ficha satisfechos.
PR: enlace.
Verificación local: comandos ejecutados y resultado real.
CI: enlace y resultado del commit entregado.
Evidencia: docs/evidencias/Txx.md, cuando corresponda.
Pendientes: solo límites o accesos que de verdad falten.
Siguiente tarea elegible: ID y dependencias comprobadas.
```

T02 · 2026-10-21
Resultado: catálogo autónomo de 88 geografías, nueve rubros y 792 IDs INEGI
verificados; comando offline; fixtures originales de México, Jalisco y
Guadalajara con manifiesto y evidencia del formato de fuente.
PR: [#4](https://github.com/guadaloop-07/mexico-inflacion-lab/pull/4).
Verificación local: `uv sync --locked`; ambas entradas de `catalogo validar`;
`make test` (12 passed); `make check` (todos los hooks pasan).
CI: [`Calidad` pasó](https://github.com/guadaloop-07/mexico-inflacion-lab/actions/runs/39645061955/job/119378327017)
en el commit `2ff1492`.
Evidencia: `docs/evidencias/T02.md`; los hashes de los fixtures se comprueban en
la suite offline.
Pendientes: ninguna; PR integrado como `5a75488` el 2026-10-21.
Siguiente tarea elegible: T03 y T04, después de integrar T02.

T03 · 2026-10-21
Resultado: siete tablas PostgreSQL con claves, FKs, restricciones e índices;
migración Alembic inicial inmutable; Compose PostgreSQL 18; registro repetible
del catálogo; y CI con PostgreSQL y pruebas de integración aisladas.
PR: [#5](https://github.com/guadaloop-07/mexico-inflacion-lab/pull/5).
Verificación local: `make check`; `make test` (14 passed); `make test-db` (3
passed) contra PostgreSQL 18, después de crear el esquema desde una base vacía.
CI: [`Calidad` pasó](https://github.com/guadaloop-07/mexico-inflacion-lab/actions/runs/39679599666)
en el commit `8b81d23`.
Evidencia: `docs/evidencias/T03.md`, incluida la persistencia tras recrear el
contenedor sin borrar su volumen.
Pendientes: ninguna; PR integrado como `1ee6bc8` el 2026-10-22.
Siguiente tarea elegible: T04; T05 requiere T03 y T04.

T04 · 2026-10-22
Resultado: extracción agrupada de las 88 geografías; parser CSV estricto con
fechas mensuales y `Decimal`; originales y manifiesto atómicos por ejecución;
y `etl fetch` sin publicación en base.
PR: [#6](https://github.com/guadaloop-07/mexico-inflacion-lab/pull/6).
Verificación local: `make check` (todos los hooks pasan); `make test` (25
pruebas pasan, sin red ni base).
CI: [`Calidad` pasó](https://github.com/guadaloop-07/mexico-inflacion-lab/actions/runs/39825865071)
en el commit `59aeaef`.
Evidencia: `docs/evidencias/T04.md`.
Pendientes: no se realizó descarga viva en T04; T05 intentará el bootstrap.
Siguiente tarea elegible: T05 después de integrar T04.

T05 · 2026-10-25
Resultado: validación de cobertura, bloqueo de escritor, publicación atómica,
idempotencia y auditoría de correcciones; comandos para bootstrap, refresh y
reconcile.
PR: [#7](https://github.com/guadaloop-07/mexico-inflacion-lab/pull/7).
Verificación local: 30 pruebas unitarias y seis de integración pasan; incluye
rollback y exclusión de escritor concurrente en PostgreSQL 18.
CI: [`Calidad` pasó](https://github.com/guadaloop-07/mexico-inflacion-lab/actions/runs/40226713286)
en el commit `efb64b5`.
Evidencia: `docs/evidencias/T05.md`.
Pendientes: el bootstrap real recibió HTTP 500 en las 88 respuestas; no se
publicaron observaciones y D1 permanece pendiente de recuperar la fuente.
Siguiente tarea elegible: ninguna hasta realizar una publicación completa válida.

T01 · 2026-10-21
Resultado: paquete instalable `inflacion_lab`, CLI con ayuda y versión,
configuración tipada sin conexiones al importar, pytest y ejecución de pruebas
unitarias dentro de `Calidad`.
PR: [#3](https://github.com/guadaloop-07/mexico-inflacion-lab/pull/3).
Verificación local: `uv sync --locked`; ayuda y versión mediante ambas entradas;
`make test` (7 passed); `make check` (todos los hooks pasan).
CI: [`Calidad` pasó](https://github.com/guadaloop-07/mexico-inflacion-lab/actions/runs/39635584104/job/119345018683)
en el commit `0c38652`.
Evidencia: las comprobaciones son reproducibles mediante los comandos anteriores;
no se requirió fuente, base ni credenciales.
Pendientes: confirmar CI e integración del PR.
Siguiente tarea elegible: T02, después de integrar T01.

## Decisiones posteriores

| Fecha | Decisión | Motivo / evidencia | Contratos afectados |
|---|---|---|---|
| 2026-10-20 | ETL completo desde la primera carga | Preferencia explícita de la propietaria | Producto, datos, T02–T05 |
| 2026-10-20 | Aprobación externa opcional | Desarrollo individual | Flujo de Git existente |
