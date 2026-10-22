# Seguimiento

Estado al redactar el plan: solo la base de Git/CI está integrada. Todas las
tareas de aplicación están pendientes. Este documento se actualiza con evidencia
real; una dependencia se considera cumplida después de confirmar su merge.

Estados: `pendiente`, `en curso`, `PR abierto`, `integrada`, `bloqueada`.

| ID | Estado | PR / commit integrado | Evidencia y limitaciones |
|---|---|---|---|
| T01 | integrada | [#3](https://github.com/guadaloop-07/mexico-inflacion-lab/pull/3) / `6a926f8` | Paquete y CLI base; `make test` (7 pruebas) y `make check` pasan localmente. `Calidad` pasó en CI. Integrada el 21 de octubre de 2026. |
| T02 | PR abierto | [#4](https://github.com/guadaloop-07/mexico-inflacion-lab/pull/4) / `928882d` | Catálogo de 792 identidades y fixtures oficiales; `make test` (12 pruebas) y `make check` pasan localmente. `Calidad` pasó en CI. |
| T03 | pendiente | — | — |
| T04 | PR abierto | [#6](https://github.com/guadaloop-07/mexico-inflacion-lab/pull/6) / `8ac4ac7` | Extracción agrupada, parser y originales atómicos; verificación local completa. `Calidad` pendiente. |
| T05 | pendiente | — | D1 exige las 792 series desde la primera publicación |
| T06 | pendiente | — | — |
| T07 | pendiente | — | — |
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
Pendientes: confirmar CI e integración del PR.
Siguiente tarea elegible: T03 y T04, después de integrar T02.

T04 · 2026-10-22
Resultado: extracción agrupada de las 88 geografías; parser CSV estricto con
fechas mensuales y `Decimal`; originales y manifiesto atómicos por ejecución;
y `etl fetch` sin publicación en base.
PR: [#6](https://github.com/guadaloop-07/mexico-inflacion-lab/pull/6).
Verificación local: `make check` (todos los hooks pasan); `make test` (25
pruebas pasan, sin red ni base).
CI: pendiente para el commit entregado.
Evidencia: `docs/evidencias/T04.md`.
Pendientes: revisión de CI; no se realizó descarga viva.
Siguiente tarea elegible: T05 después de integrar T03 y T04.

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
