# T06 · Cálculos canónicos e independientes

Dependencias: T05. Rama sugerida: `feat/t06-metricas`.

## Objetivo

Crear las medidas que utilizarán API, gráficas y CSV, con evidencia de que fechas,
denominadores y precisión son correctos.

## Leer

`AGENTS.md`, `../ejecucion.md`, cálculos de `../api.md`, `../datos.md` y
`../validacion.md`.

## Implementar

- Consultas/vistas canónicas para índice, tasa mensual, tasa anual, razón entre
  índices y diferencia de tasas. Versionar las vistas con Alembic.
- Joins por mes exacto de la misma serie; calcular antes de filtrar el rango.
- Resultados tipados con unidad, valor y motivo cuando sea nulo.
- Pruebas de integración con una tabla sintética de resultados conocidos,
  calculados de forma independiente de la consulta SQL.
- Contraste de una muestra oficial mensual/anual de México, Jalisco y
  Guadalajara; documentar serie, mes, fuente, fórmula y precisión publicada en
  `docs/evidencias/T06.md`. Incluir un intervalo relevante de cambio metodológico
  cuando sea verificable, usando las series oficiales enlazadas.

## Aceptación y comprobación

- Eliminar un mes de una fixture no desplaza el denominador anual a otro mes.
- Recortar la historia a los últimos meses no borra denominadores existentes.
- 2018 muestra anual sin denominador de 2017; no se rellena con cero.
- Tasas negativas y tasas exactamente cero se conservan correctamente.
- Un índice nulo o ausente produce el motivo esperado; no se aceptan índices
  cero como observaciones válidas.
- Las diferencias se expresan en puntos porcentuales. El acumulado usa razón,
  no suma de tasas. No se fabrica un nacional a partir de geografías.
- `make check`, `make test`, `make test-db` y CI pasan.

Esta tarea amerita una revisión focalizada de fórmulas antes de integrar. No
añadir pronósticos ni contribuciones sin sus fuentes y definiciones propias.
