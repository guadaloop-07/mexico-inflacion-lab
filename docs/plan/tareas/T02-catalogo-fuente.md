# T02 · Catálogo de las 792 series y evidencia de fuente

Dependencias: T01. Rama sugerida: `feat/t02-catalogo-fuente`.

## Objetivo

Fijar las identidades de todas las series y el formato real que debe soportar el
parser. Esta tarea incluye verificaciones de lectura contra el INEGI.

## Leer

`AGENTS.md`, `../ejecucion.md`, `../datos.md` y `../fuentes.md`.
Consultar los extractores locales de referencia solo donde aporten catálogo o
parámetros. El resultado debe funcionar sin esos repositorios instalados.

## Implementar

- `config/series.yml` autónomo y validación tipada en `catalogo.py`.
- 88 geografías, nueve rubros y 792 IDs explícitos; nombres completos, frecuencia,
  clasificación, referencia del índice y URL de procedencia.
- Comando `inflacion-lab catalogo validar`, completamente offline.
- Contrastar identidades y etiquetas con los metadatos oficiales accesibles;
  registrar el método y las diferencias, sin inventar IDs derivados.
- Obtener exportaciones acotadas de México, Jalisco y Guadalajara con los nueve
  índices y al menos 24 meses cerrados, incluyendo denominadores verificables.
- Incluir fixtures pequeños originales en `tests/fixtures/inegi/` y un manifiesto
  con URL, parámetros sanitizados, fecha, hash, codificación y contenido esperado.
  Conservar metadatos suficientes para identificar columnas; no fabricar fixtures
  que solo reproduzcan el formato deseado por el programador.
- Documentar formulario, encabezados, delimitador, nulos y correspondencia
  columna-serie en `docs/evidencias/T02.md`; ajustar el contrato si la evidencia
  real lo exige. Referenciar la metodología y calendario vigentes verificables.

## Aceptación y comprobación

- Validación offline exige unicidad y total 9 + 288 + 495 = 792.
- Tests rechazan serie duplicada, estructura inválida y rubro/geografía faltante.
- Las muestras se identifican como oficiales con fecha congelada. Datos
  sintéticos de casos límite se almacenan separados y rotulados.
- Se distingue la verificación del catálogo completo de la revisión de valores
  en tres ubicaciones; no se afirma haber contrastado todos los valores.
- `make check` y `make test` pasan offline. El reporte enumera qué consultas
  vivas se ejecutaron y cualquier identidad pendiente de resolver.

Una discrepancia que cambie la cobertura exige evidencia y decisión documentada
antes de D1; no se resuelve reduciendo silenciosamente el catálogo.
