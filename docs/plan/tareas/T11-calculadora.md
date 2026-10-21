# T11 · Calculadora de monto actualizado

Dependencias: T09, T10. Rama sugerida: `feat/t11-calculadora`.

## Objetivo

Responder cuánto dinero en el mes final equivale aproximadamente al monto del
mes inicial según el índice general de la geografía seleccionada.

## Leer

`AGENTS.md`, `../ejecucion.md`, calculadora y fórmulas de `../api.md`,
`../interfaz.md` y `../validacion.md`.

## Implementar

- Endpoint `/calculadora` con validación de monto y meses; reutilizar el cálculo
  decimal del backend y el índice general de la geografía elegida.
- Formulario accesible con fechas independientes, formato de pesos y explicación
  del resultado. Monto inicial predeterminado de 1,000 pesos.
- Resultado con monto original/actualizado, meses e índices usados y variación
  acumulada; fuente y versión recuperables.
- Mantener el monto en memoria, sin añadirlo a parámetros de URL ni a logs.
- Estados de índices faltantes y mensajes de error sin estimaciones inventadas.

## Aceptación y comprobación

- Índices sintéticos 100 → 110 convierten 1,000 a 1,100; operación inversa y mismo
  mes dan sus resultados exactos dentro de la precisión definida.
- Fecha invertida, monto no positivo o excesivo y precisión inválida se rechazan
  en servidor. Un índice faltante devuelve nulo con motivo.
- No sumar inflación mensual ni calcular por segunda vez la razón en TypeScript.
- Tests API y de formulario; comprobación manual del lenguaje y uso por teclado.
- `make check`, suites Python/DB/web, build y CI pasan.

El resultado se presenta como actualización por el INPC, no como presupuesto
personal ni recomendación de inversión.
