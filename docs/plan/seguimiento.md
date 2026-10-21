# Seguimiento

Estado al redactar el plan: solo la base de Git/CI está integrada. Todas las
tareas de aplicación están pendientes. Este documento se actualiza con evidencia
real; una dependencia se considera cumplida después de confirmar su merge.

Estados: `pendiente`, `en curso`, `PR abierto`, `integrada`, `bloqueada`.

| ID | Estado | PR / commit integrado | Evidencia y limitaciones |
|---|---|---|---|
| T01 | pendiente | — | — |
| T02 | pendiente | — | — |
| T03 | pendiente | — | — |
| T04 | pendiente | — | — |
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

## Decisiones posteriores

| Fecha | Decisión | Motivo / evidencia | Contratos afectados |
|---|---|---|---|
| 2026-10-20 | ETL completo desde la primera carga | Preferencia explícita de la propietaria | Producto, datos, T02–T05 |
| 2026-10-20 | Aprobación externa opcional | Desarrollo individual | Flujo de Git existente |
