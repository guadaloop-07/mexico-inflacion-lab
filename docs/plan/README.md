# Plan de ejecución

Fecha: 20 de octubre de 2026. Base revisada: `main`, commit `f4e9ae4`.
Este documento describe trabajo futuro; las funciones de aplicación todavía no
están implementadas. La configuración de Git y CI ya está integrada.

## Estrategia

Un repositorio, una base de datos y una aplicación desplegable en un servidor.
**El primer ETL incorpora las 792 series del catálogo actual**: nacional, 32
entidades y 55 ciudades, con índice general y ocho rubros por ubicación.
Las primeras vistas serán pequeñas, pero consumirán esa carga completa.

El orden es: verificar la fuente, cargar y publicar los datos completos, validar
los cálculos, exponer consultas y construir la experiencia de exploración.
Cada tarea termina en un PR que puede ejecutar un modelo con contexto reducido.

## Documentos que gobiernan la implementación

| Documento | Decisiones que contiene |
|---|---|
| [Producto](producto.md) | Público, preguntas, alcance y condiciones de lanzamiento |
| [Arquitectura](arquitectura.md) | Tecnologías, estructura y límites de componentes |
| [Datos](datos.md) | Catálogo, extracción, esquema y publicación completa |
| [API](api.md) | Cálculos, rutas, parámetros y semántica de respuestas |
| [Interfaz](interfaz.md) | Composición, controles, estados y accesibilidad |
| [Validación](validacion.md) | Pruebas y evidencias requeridas |
| [Operación](operacion.md) | Actualización, despliegue, respaldos y recuperación |
| [Ejecución](ejecucion.md) | Cómo entregar una tarea al modelo ejecutor |
| [Seguimiento](seguimiento.md) | Estado de tareas y registro de entregas |
| [Fuentes](fuentes.md) | Referencias técnicas y evidencia pendiente de verificar |

Los contratos de datos y API prevalecen sobre ejemplos informales. Si la fuente
real contradice un supuesto, conserva la evidencia y corrige el contrato en el
PR correspondiente; una discrepancia no autoriza inventar valores ni cambiar
silenciosamente el significado de una serie.

## Entregas

| Entrega | Condición de salida |
|---|---|
| D1 · Datos confiables | T01–T05: primer bootstrap con las 792 series validadas; publicación atómica e idempotente |
| D2 · Primera experiencia | T06–T08: API y gráfica nacional alimentadas por D1; comprobación independiente de tasas |
| D3 · Laboratorio completo | T09–T11: comparaciones, rubros, CSV y calculadora, con datos de las 88 geografías |
| D4 · Publicación operable | T12–T16: actualización, contenedores, verificación integral, restauración y despliegue |
| D5 · Ajustes de uso | T17: revisión del primer ciclo de publicación y mejoras basadas en observaciones |

## Tareas, en orden recomendado

Los identificadores son estables. Las dependencias son PRs integrados en `main`,
no ramas locales todavía sin integrar. Ejecutar una tarea por vez es el valor
predeterminado para este proyecto individual.

| ID | Tarea | Depende de |
|---|---|---|
| [T01](tareas/T01-base-python.md) | Paquete Python, configuración y pruebas | Base de Git existente |
| [T02](tareas/T02-catalogo-fuente.md) | Catálogo completo y verificación de fuente | T01 |
| [T03](tareas/T03-postgres.md) | Postgres, migraciones y aislamiento de pruebas | T02 |
| [T04](tareas/T04-extraccion.md) | Descarga CSV agrupada y parser de las 792 series | T02 |
| [T05](tareas/T05-publicacion.md) | Validación, carga completa y revisiones | T03, T04 |
| [T06](tareas/T06-calculos.md) | Cálculos canónicos de inflación | T05 |
| [T07](tareas/T07-api-base.md) | API de catálogo, resumen e historia | T06 |
| [T08](tareas/T08-web-inicial.md) | Primera gráfica web y herramientas frontend | T07 |
| [T09](tareas/T09-api-exploracion.md) | API de comparación, rubros y exportación | T07 |
| [T10](tareas/T10-exploracion-web.md) | Exploración geográfica y de rubros | T08, T09 |
| [T11](tareas/T11-calculadora.md) | Actualización de montos por INPC | T09, T10 |
| [T12](tareas/T12-actualizacion.md) | Actualización programable y frescura | T05, T09 |
| [T13](tareas/T13-contenedores.md) | Empaquetado para el servidor | T10, T11, T12 |
| [T14](tareas/T14-validacion-integral.md) | Pruebas integrales y revisión de uso | T13 |
| [T15](tareas/T15-respaldos.md) | Respaldo, restauración y recuperación | T13 |
| [T16](tareas/T16-despliegue.md) | Despliegue e integración con el sitio | T12, T14, T15; datos del servidor |
| [T17](tareas/T17-primer-ciclo.md) | Revisión del primer ciclo operativo | T16; una publicación mensual real |

T03 y T04 son técnicamente independientes después de T02. Eso permite cambiar
su orden sin modificar los contratos; no exige trabajo simultáneo de agentes.

## Decisiones que todavía necesita aportar la propietaria

Estas decisiones afectan T16, no impiden empezar T01–T15:

- Servidor y acceso autorizado, sistema operativo, arquitectura y recursos.
- Dominio y forma de integración con el sitio existente. Se prepara por defecto
  `/inflacion/` para la web y `/api/inflacion/v1` para la API, en el mismo origen.
- Proxy existente, puertos disponibles y usuario de servicio.
- Destino externo del respaldo y mecanismo autorizado para informar fallos.

No se contratarán servicios ni se cambiará infraestructura externa como parte de
la planeación. T16 deja una barrera explícita para las acciones de despliegue.

## Próximo paso

Después de integrar este plan, pasar al modelo ejecutor el prompt de
[ejecucion.md](ejecucion.md) con `T01`. La entrega completa se divide en los PRs
anteriores; no se pide a un solo prompt que construya todo el producto.
