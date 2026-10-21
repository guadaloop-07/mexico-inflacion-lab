# T14 · Validación integral y experiencia

Dependencias: T13. Rama sugerida: `feat/t14-verificacion-integral`.

## Objetivo

Comprobar el recorrido completo y las condiciones de producto antes de publicar,
incluyendo calidad de interpretación y funcionamiento en móvil.

## Leer

`AGENTS.md`, `../ejecucion.md`, `../producto.md`, `../validacion.md`,
`../interfaz.md` y los contratos de datos/API.

## Implementar

- Playwright con Chromium y comando `make test-e2e`. Entorno aislado con DB
  `_test`, API y web construida; carga reproducible desde fixtures atribuidos.
- En CI, preparar navegador/servicios y ejecutar la suite dentro del check
  obligatorio. Ajustar timeout solo por necesidades demostradas del pipeline.
- Casos de usuario: resumen, cambio de ubicación, comparación, rubros,
  calculadora, enlace compartido y CSV. Incluir fallos y nulos significativos.
- Caso integral de refresh fallido que conserva la publicación anterior.
- Revisión semántica de nombres, unidades, explicaciones y precisión.

## Aceptación y comprobación

- E2E no usa la red del INEGI ni datos ficticios como fallback del producto.
- CSV y gráfica coinciden para la misma selección; corte común en comparación.
- Las vistas no conectan huecos ni convierten nulos en ceros.
- Inspección visual en 360/768/1280 px; teclado, foco, contraste y tablas
  accesibles. El reporte registra qué se inspeccionó, además del build.
- Medir respuestas y carga de página en el entorno documentado; identificar
  consultas lentas o recursos innecesarios con evidencia, sin tests de tiempo
  arbitrarios que vuelvan inestable el CI.
- Proponer tres sesiones breves con personas poco experimentadas; registrar
  hallazgos o la falta de participantes como limitación, sin inventar respuestas.
- `make check`, todas las suites, build y CI pasan. Evidencia en
  `docs/evidencias/T14.md`, incluyendo omisiones materiales pendientes.

Reparar defectos dentro de los contratos. Cambios sustanciales de alcance se
documentan antes de ampliar esta tarea.
