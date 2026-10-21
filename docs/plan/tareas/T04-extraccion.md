# T04 · Extracción agrupada y parser completo

Dependencias: T02. Rama sugerida: `feat/t04-extraccion`.

## Objetivo

Descargar las 88 exportaciones y convertir las 792 series a registros tipados,
con originales recuperables y fallos explícitos. La publicación llega en T05.

## Leer

`AGENTS.md`, `../ejecucion.md`, `../datos.md`, `../validacion.md` y la evidencia
T02 integrada.

## Implementar

- httpx síncrono y cliente reutilizable según el formulario demostrado en T02.
- Cliente con timeouts, reintentos limitados, pausa entre ubicaciones y validación
  de contenido. Recibe las series explícitas del catálogo y agrupa por ubicación.
- Parser de bytes CSV a registros `Decimal`/`date` con vínculo semántico de
  columnas. Tolera orden diferente; rechaza ambigüedad o formato desconocido.
- Originales y manifiesto por ejecución; escritura temporal antes de reemplazo,
  hashes y logs sin secretos. Distinguir archivo fallido de archivo completo.
- Comando `inflacion-lab etl fetch`: descarga el catálogo completo y genera un
  informe, sin escribir observaciones ni declarar D1 publicada.
- Interfaces pequeñas para que T05 reutilice transporte y parseo directamente.

## Aceptación y comprobación

- Los tres fixtures reales se convierten con IDs/rubros correctos y nulos
  preservados. Una columna reordenada no cambia su identidad.
- Tests mockean HTTP: timeout, 429, error persistente y HTML con estado 200.
- Tests rechazan columna desconocida, duplicada, token no numérico desconocido,
  fecha inválida y clave duplicada.
- `etl fetch` intenta las 88 ubicaciones, informa cobertura esperada de 792 y
  sale con error si alguna descarga o identificación falla; no produce éxito
  parcial como resultado final.
- `make check` y `make test` pasan offline. Una comprobación viva, si se ejecuta,
  se registra aparte y los originales completos permanecen fuera de Git.

No incorporar un modo de producto limitado a una serie. Los catálogos mínimos
inyectados por tests únicamente verifican casos aislados.
