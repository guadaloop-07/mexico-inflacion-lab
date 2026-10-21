# Operación y despliegue

## Entornos

| Entorno | Datos y permisos |
|---|---|
| Unitario | Fixtures; sin red ni base |
| Integración/CI | PostgreSQL 18 desechable; nombre de base terminado en `_test` |
| Desarrollo | Base local y carga real completa; archivos fuera de Git |
| Verificación de despliegue | Compose local/separado; fixtures o snapshot atribuido |
| Producción | Catálogo y carga completos; API de lectura; respaldos externos |

Los originales y bases reales no se suben a Git. Las pruebas no apuntan a
producción ni descargan de INEGI durante cada PR.

## Actualización programada

Valor inicial: una ejecución diaria a las 10:00 en `America/Mexico_City` con
`refresh`, y reconciliación histórica completa el día 15 a las 11:00.
La cadencia es una decisión operativa revisable en T17; no pretende representar
el calendario de publicación del INEGI.

Cada ejecución consulta las 88 geografías y publica las 792 series dentro de su
ventana. El primer arranque usa `bootstrap`, desde 2018. Si no cambian los
valores, informa `sin_cambios`; no afirma que exista un nuevo mes de datos.

T12 prepara comandos y unidades systemd/timers, sin activarlos en un servidor
desconocido. T16 los instala en el destino acordado. En otro sistema operativo,
T16 documenta el mecanismo equivalente. La API no ejecuta jobs programados.

Los escritores se excluyen mediante bloqueo asesor. Un job que encuentra otro
activo informa esa condición, sin fingir éxito de actualización. Las unidades
tienen reintento limitado y no acumulan ejecuciones simultáneas.

## Frescura y observabilidad

Separar:

- Último intento y su resultado.
- Última carga validada/publicada.
- Último periodo observado por serie y nivel.
- Próxima publicación esperada, solo si se cargó un calendario oficial vigente.

La frescura no se deriva únicamente de la edad del último intento. T12 registra
el calendario y fuente del año operativo en un archivo de configuración
versionado. Si no está verificado, muestra `calendario_no_verificado`, en lugar
de inventar una fecha. El siguiente año requiere actualizarlo.

Logs estructurados a stdout con ejecución, componente, duración, conteos,
periodos, reintentos y errores sanitizados. La respuesta pública no contiene
rutas locales ni credenciales. Se mantiene un comando `etl status` que distingue
fallo operativo, ausencia de cambios y atraso respecto al calendario verificado.

Las notificaciones de fallos necesitan un canal y destinatario elegidos por la
propietaria. Hasta entonces se preparan logs y estado consultable, sin enviar
mensajes ni crear integraciones externas.

## Contenedores

Servicios objetivo: `db`, `api`, `web` y ejecución puntual `etl` con la imagen de
API. Un comando separado ejecuta las migraciones con su rol antes de actualizar
la aplicación. No iniciar migraciones competitivas desde cada worker.

Builds repetibles con `uv.lock` y `npm ci`. Runtime sin compiladores ni paquetes
de desarrollo cuando sea viable. API/web como usuarios sin privilegios; límites
y healthchecks; originales en volumen persistente. La base no publica su puerto
en producción. Los puertos locales de desarrollo se enlazan a localhost.

Se fijan versiones/digests de imágenes al implementarlas. PostgreSQL 18 utiliza
la disposición de volúmenes documentada para esa imagen; verificar explícitamente
el montaje en `/var/lib/postgresql` y la persistencia tras recrear el contenedor.
No copiar automáticamente un montaje de una versión anterior de Postgres.

El proxy existente termina HTTPS y envía rutas de web/API al servicio respectivo.
Los archivos estáticos con hash admiten caché larga; HTML, caché corta. Una URL
de API desconocida devuelve un error de API, no el HTML de la página.

## Acceso a Postgres

- Rol de migración: propietario de objetos, utilizado en operaciones de esquema.
- Rol ETL: escritura de tablas del dominio y ejecución de sus consultas; sin
  privilegios de crear roles o administrar otras bases.
- Rol API: SELECT y permisos de conexión/esquema necesarios. Se prueba que no
  puede modificar observaciones.

T03 permite un rol local de desarrollo para construir el esquema. T13 incorpora
la separación de roles y sus pruebas para el despliegue. Las contraseñas reales
se aprovisionan por entorno y no se incrustan en SQL versionado.

## Respaldo y restauración

Objetivos iniciales: pérdida máxima de 24 horas de cambios propios y recuperación
en cuatro horas. Son objetivos a medir en T15, no garantías del plan.

- Dump diario en formato custom con herramientas compatibles con Postgres 18.
- Copia externa cifrada del dump, catálogo/versión y originales/manifiestos.
- Retención inicial propuesta: siete diarios, cuatro semanales y tres mensuales.
- Originales de ejecuciones exitosas conservados en v1; medir su crecimiento
  antes de introducir limpieza. Un manifiesto no reemplaza al archivo de origen.
- Coordinar el respaldo con el bloqueo del ETL para que el dump no referencie
  originales todavía ausentes de la copia. Documentar el tiempo de bloqueo.
- Verificar integridad y restaurar periódicamente en una base `_test`, con un
  directorio de originales separado.

La restauración comprueba catálogo, conteos, hashes de archivos referenciados,
tasas conocidas, API de lectura y estado de última publicación. El dump no
reemplaza la configuración de roles ni el acceso a las claves de cifrado.

Un respaldo en el mismo disco es una copia local de trabajo, no satisface la
condición de copia externa. T15 puede probar todo localmente y dejar pendiente
el destino externo; T16 verifica ese destino antes de declarar el lanzamiento.

## Publicación y rollback

1. Obtener del propietario los datos de servidor/dominio/proxy y alcance de
   acceso. Inspeccionar configuración existente antes de proponer modificaciones.
2. Registrar versión de aplicación e imágenes; preparar respaldo verificado.
3. Ejecutar migraciones compatibles, levantar servicios y bootstrap completo.
4. Probar rutas en el destino de verificación, luego integrar con el sitio según
   el acceso autorizado. Activar HTTPS y timers.
5. Verificar la URL pública, versión, fuente, filtros, CSV, reinicio y respaldo.

Para volver de versión se conserva la imagen/configuración anterior. Los cambios
de esquema de v1 procuran ser compatibles con esa versión. No se ejecuta un
downgrade destructivo de base como respuesta automática a una falla de la web.
Una recuperación de datos real requiere identificar el respaldo y destino
exactos y actuar dentro del alcance autorizado.

T16 puede completar archivos y ensayo local antes de tener acceso al servidor.
Debe informar qué validaciones remotas faltan, sin presentar ese ensayo como un
despliegue público realizado.
