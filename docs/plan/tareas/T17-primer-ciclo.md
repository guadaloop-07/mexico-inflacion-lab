# T17 · Revisión del primer ciclo operativo

Dependencias: T16 y una publicación mensual real posterior al despliegue.
Rama sugerida: `docs/t17-primer-ciclo`; correcciones en PRs específicos.

## Objetivo

Comprobar que el laboratorio sigue siendo confiable al pasar de la carga inicial
a una nueva publicación y decidir mejoras a partir de evidencia de uso.

## Leer

`AGENTS.md`, `../ejecucion.md`, `../producto.md`, `../operacion.md` y evidencias
del despliegue y actualizaciones efectivamente realizadas.

## Revisar

- Cuándo la fuente publicó el siguiente mes y cuándo lo mostró el laboratorio.
- Cobertura de las 792 series, nulos, cambios de metadatos y revisiones detectadas.
- Fallos/reintentos, duración y consumo observados, crecimiento de originales,
  éxito del respaldo y resultado de restauración.
- Consultas lentas y errores reales de interacción, sin inventar analítica de
  visitantes que no se haya recolectado ni añadir rastreo por defecto.
- Hallazgos de las sesiones de uso si existieron.

## Aceptación

Un reporte breve en `docs/evidencias/T17.md` separa hechos, limitaciones y mejoras
priorizadas. Proponer como máximo tres siguientes cambios con problema, evidencia
y criterio de aceptación. Revisar la cadencia diaria/mensual si los resultados lo
justifican. No declarar completo este ciclo antes de que llegue esa publicación.

Esta ficha es una revisión futura y acotada. El plan no activa un agente de
monitoreo indefinido ni envía mensajes a otras personas.
