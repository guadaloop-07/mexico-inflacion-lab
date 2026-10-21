# T09 · Comparación, rubros y CSV

Dependencias: T07. Rama sugerida: `feat/t09-api-exploracion`.

## Objetivo

Proveer las consultas de exploración de las 88 geografías y un CSV que corresponda
exactamente a la selección de las vistas.

## Leer

`AGENTS.md`, `../ejecucion.md`, `../api.md`, `../datos.md` y `../validacion.md`.

## Implementar

- `/comparacion`, `/rubros` y `/exportacion.csv` con las selecciones y límites
  descritos en el contrato. Mantener los servicios de cálculo ya verificados.
- Rejilla mensual de comparación, máximo cuatro geografías, un corte común y
  participantes sin dato conservados como nulos.
- Ocho rubros, excluyendo general, con nombres completos y estados explícitos.
- CSV con orden, precisión, versión y fuente del contrato; nombres de archivo
  seguros y errores coherentes con las rutas JSON.
- OpenAPI y ejemplos ilustrativos claramente identificados.

## Aceptación y comprobación

- Una comparación nacional/estatal/ciudad contiene el mismo intervalo y corte;
  si a una le falta el mes, no se utiliza otro mes para sustituirlo.
- El máximo de participantes y rango se valida antes de consultar.
- Tests contrastan CSV con las respuestas JSON del mismo filtro, incluyendo
  nulos, tasas negativas y filtros con solo un participante.
- Cambiar rubro, fecha o geografía cambia las observaciones y el ETag apropiados.
- Las consultas múltiples usan una versión coherente y conservan la procedencia.
- `make check`, `make test`, `make test-db` y CI pasan.

No producir contribuciones a la inflación a partir del ranking de tasas.
