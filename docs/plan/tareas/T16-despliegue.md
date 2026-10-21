# T16 · Despliegue e integración con el proyecto

Dependencias: T12, T14, T15 y datos del destino. Rama sugerida:
`chore/t16-despliegue`.

## Objetivo

Publicar el laboratorio en el servidor y sitio acordados y verificar operación
real, incluyendo carga completa, actualización y respaldo externo.

## Leer

`AGENTS.md`, `../ejecucion.md`, `../operacion.md`, condiciones de lanzamiento de
`../producto.md` y evidencias T05/T14/T15.

## Datos que se necesitan de la propietaria

- Servidor, acceso autorizado y alcance concreto del despliegue.
- SO, arquitectura, recursos, proxy/puertos y usuario de servicio.
- Dominio y ruta o subdominio; acceso a DNS/TLS si hace falta modificarlo.
- Destino/credenciales del respaldo externo y custodia de clave de recuperación.
- Canal de aviso de fallos, si se desea activar notificaciones.

Antes de preguntar, consultar la configuración existente autorizada que pueda
resolver esos datos. Un dato imprescindible ausente bloquea solo su acción
dependiente: completar primero archivos, runbook y ensayo local revisables.
Implementar esta ficha no autoriza contratar servicios ni modificar otros sitios.

## Implementar y verificar

- Registrar commit/imágenes y configuración del destino sin secretos.
- Integración con proxy existente, HTTPS y rutas acordadas. Ajustar el build base
  si cambia la decisión de `/inflacion/`.
- Migraciones, roles, volúmenes y bootstrap completo de 792 series verificado.
- Arranque/reinicio, timers y logs. Confirmar que una descarga fallida conserva
  el último estado válido también en ese entorno.
- Copia cifrada externa y restauración comprobada de acuerdo con T15.
- Abrir la URL publicada y probar filtros, cálculos, comparación, CSV, errores y
  uso móvil. Confirmar fuente, periodo y versión reales.
- Documentar actualización y regreso a imagen anterior. No automatizar un
  downgrade destructivo de base para resolver un fallo de aplicación.

## Aceptación

`docs/evidencias/T16.md` registra URL, versión, checks y pendientes reales. Se
declara D4 cuando el servicio público está verificado y cuenta con actualización
y recuperación. Un build local por sí solo no satisface este resultado.

Concluir con enlace público y runbook, o con el acceso exacto que falte. Actualizar
README y seguimiento sin exponer secretos ni detalles sensibles del servidor.
