# Contrato de datos y ETL

## Identidad y cobertura

La unidad de observación es **una serie mensual, una ubicación y un mes**. Cada
serie corresponde a una combinación de geografía y rubro. El índice es un nivel
publicado; su variación porcentual se calcula después.

| Nivel | Geografías | Series por geografía | Series esperadas |
|---|---:|---:|---:|
| Nacional | 1 | 9 | 9 |
| Entidad | 32 | 9 | 288 |
| Ciudad INPC | 55 | 9 | 495 |
| Total | 88 | 9 | 792 |

Este total define el alcance inicial solicitado. Si la fuente demuestra un
cambio de catálogo, T02 debe explicar y resolver la diferencia antes de aprobar
el primer bootstrap; no se declara éxito contando solo descargas realizadas.

Identificadores públicos: `mx`, `entidad-01` a `entidad-32`, y `ciudad-01` a
`ciudad-55`. Los códigos de ciudad son los del catálogo del INPC; no se asumen
equivalentes a municipios. ZMVM no se fuerza a pertenecer a una sola entidad.

| ID de rubro | Etiqueta |
|---|---|
| `general` | Índice general |
| `alimentos_bebidas_tabaco` | Alimentos, bebidas y tabaco |
| `ropa_calzado_accesorios` | Ropa, calzado y accesorios |
| `vivienda` | Vivienda |
| `muebles_aparatos_accesorios` | Muebles, aparatos y accesorios domésticos |
| `salud_cuidado_personal` | Salud y cuidado personal |
| `transporte` | Transporte |
| `educacion_esparcimiento` | Educación y esparcimiento |
| `otros_servicios` | Otros servicios |

Las etiquetas se contrastan con las exportaciones antes de fijar sus alias.
El catálogo conserva `id_estructura`, `id_serie_inegi`, etiqueta de fuente,
geografía, rubro, frecuencia, periodo de referencia del índice, clasificación,
límites conocidos de cobertura, URL de fuente y fecha de verificación.
Todos los IDs del proveedor se tratan como cadenas.

El catálogo YAML existente sirve de referencia, no de comprobación semántica.
El modelo publicado no depende de rutas absolutas de otros repositorios. Se
incluye aquí un catálogo autónomo y se registra de dónde se obtuvo.

## Fuente y descarga

Se utiliza el exportador CSV verificado del INEGI, agrupando los nueve IDs de
cada ubicación. Un bootstrap completo implica 88 exportaciones de datos, más
las consultas de metadatos que requiera su verificación.

- Inicio: enero de 2018. Año final: calculado al ejecutar, no una constante.
- Se solicitan niveles del índice, frecuencia mensual y orientación vertical.
- Sesión HTTP reutilizable, timeout explícito de conexión y lectura, tres
  intentos para fallos de red, 408, 429 y errores transitorios 5xx.
- Respetar `Retry-After` con un límite documentado; registrar los reintentos.
- Peticiones secuenciales con pausa pequeña configurable. No lanzar 792
  peticiones simultáneas.
- Validar estado HTTP y contenido. Un HTML de error con HTTP 200 no es un CSV.
- Un fallo de formato o de identificación semántica no se reintenta como si
  fuera un problema de conexión.

El cuerpo real del formulario, codificación, delimitador y sección de metadatos
se verifican en T02. T04 implementa el formato demostrado por esas muestras.
Se detecta el encabezado por estructura y contenido validados, sin depender
exclusivamente de `skiprows` ni del orden de columnas.

Cada columna debe vincularse a su serie por ID, o por etiqueta inequívoca
contrastada con el catálogo si el CSV no expone IDs. Cambios de orden son
aceptables; nombres desconocidos, columnas duplicadas o asociaciones ambiguas
hacen fallar la validación. No se infiere un ID restando uno a otro.

## Originales y registros

Cada ejecución obtiene un UUID. Guarda bytes originales y manifiesto en
`data/raw/<uuid>/`, con nombre por geografía, SHA-256, fecha UTC, parámetros
sanitizados, cobertura solicitada y resultado de validación. La escritura de
cada archivo pasa por un temporal y reemplazo atómico.

El parser produce `serie_id`, `periodo` y `valor`, más referencia al archivo.
`periodo` es un `date` del primer día del mes. `valor` se parsea como `Decimal`.
N/E y otros marcadores demostrados en T02 se conservan como `null`; un token
desconocido produce error. No se descartan silenciosamente filas no numéricas.

## Esquema lógico

| Tabla | Clave y contenido |
|---|---|
| `geografias` | ID público, nivel, nombre, código de fuente, entidad opcional |
| `rubros` | ID estable, etiqueta y orden de presentación |
| `series` | ID interno; unicidad `(geografia_id, rubro_id)` y de identidad del proveedor; metadatos de base/frecuencia |
| `ejecuciones_etl` | UUID, modo, inicio/fin UTC, estado, versión del catálogo, conteos y error sanitizado |
| `archivos_fuente` | Ejecución, geografía, hash, ruta relativa y parámetros/cobertura |
| `observaciones` | PK `(serie_id, periodo)`, `valor NUMERIC(18,6)` nullable, archivo y ejecución de última modificación |
| `revisiones_observacion` | Serie, periodo, valor anterior/nuevo, ejecución y archivo que justifican el cambio |

Restricciones: mes representado por día 1; índice positivo cuando no es nulo;
FKs obligatorias donde aplican; niveles y estados validados. Si la fuente aporta
más de seis decimales, se modifica el contrato con evidencia antes de cargarla,
en lugar de redondear silenciosamente. No se transforma en `float` en el ETL.

Se mantienen una sola tabla de observaciones y catálogos locales. El acceso de
API a la base es de lectura. En producción, migraciones y escritura tienen
roles distintos según [operacion.md](operacion.md).

## Validación antes de publicar

1. Las 88 geografías y 792 series esperadas están representadas y vinculadas
   correctamente. Una serie con datos nulos sigue siendo una serie identificada.
2. No hay claves duplicadas, fechas inválidas, valores imposibles ni periodos
   posteriores al último mes cerrado.
3. La historia empieza en el límite solicitado o en el inicio de disponibilidad
   documentado de la serie. Se comprueban huecos interiores y meses recientes.
   El corte de una nueva publicación mensual es el último mes de general
   nacional recibido; las 792 series deben representar ese mes, aunque haya
   nulos oficiales. Un retraso sin explicación en otra serie impide publicar
   ese nuevo corte y se reintenta conservando la publicación anterior.
4. Los faltantes legítimos tienen un marcador explícito de fuente o una
   excepción documentada con evidencia. No se rellenan con cero o interpolación.
5. Una fila publicada que desaparece del intervalo recargado se investiga; no
   se interpreta automáticamente como una eliminación válida.
6. No se acepta como fresca una descarga que haya retrocedido en cobertura o
   perdido series. Las variaciones grandes se señalan para contrastarlas, sin
   descartarlas únicamente por ser grandes.

La validación devuelve un informe por serie y ejecución: esperadas, recibidas,
con valores, nulas, intervalos y errores. No exige que las 792 series tengan
exactamente el mismo primer mes ni convierte nulos legítimos en fallos.

## Publicación completa y atomicidad

La CLI ofrece `etl run --mode bootstrap|refresh|reconcile`. **Todos los modos
de producto cubren las 792 series.** No hay un parámetro de publicación parcial.
Las pruebas pueden usar catálogos mínimos aislados que no son el catálogo de
producción.

1. Registrar ejecución y adquirir un bloqueo asesor de Postgres para impedir
   dos escritores simultáneos. Mantenerlo en una conexión dedicada durante la
   ejecución, liberándolo también en caso de error.
2. Descargar y validar todo el lote fuera de la transacción de publicación.
   Conservar manifiesto y originales aunque un archivo falle.
3. Preparar tablas temporales y validar claves contra el catálogo completo.
4. En una única transacción: aplicar los cambios validados de catálogo,
   cargar/upsert, registrar cambios de valores, comprobar conteos y marcar la
   ejecución como exitosa. Una actualización de catálogo no debe adelantarse
   a los datos que describe en una publicación activa.
5. Ante cualquier error, revertir los cambios de observaciones y revisiones.
   Marcar el fallo por separado si la base está disponible y salir con código
   distinto de cero. La API sigue consultando la última versión válida.

`ON CONFLICT DO UPDATE` actualiza solo valores distintos, incluyendo transiciones
desde/hacia nulo verificadas. Las filas sin cambios conservan su origen. Repetir
el mismo lote no aumenta las observaciones ni las revisiones de valores.

La versión pública es el UUID de la última ejecución exitosa. Lecturas de datos
y metadatos de una respuesta comparten una transacción `REPEATABLE READ`, de
solo lectura; `READ COMMITTED` no garantiza el mismo snapshot entre consultas.
Una API sin carga exitosa devuelve un estado vacío explícito.

## Actualizaciones e historia

- `bootstrap`: primera carga, desde 2018, catálogo completo; se puede repetir
  sin duplicar datos.
- `refresh`: las 792 series, últimos 24 meses por defecto. El exportador recibe
  años completos cuando sea necesario y la ventana se filtra después del parseo.
  Exige una carga completa previa; no sustituye el bootstrap inicial.
- `reconcile`: historia completa desde 2018 para las 792 series.

No se usa el máximo global de ciudades para excluir meses de otras series.
La ventana comienza en el primer día del mes de referencia menos
`REFRESH_MONTHS - 1`; incluye ambos extremos. La reconciliación completa detecta
cambios anteriores a esa ventana. Su programación se define en operación.

## Evidencia de D1

Un reporte sanitizado en `docs/evidencias/T05.md` registra catálogo, commit,
ejecución, rango real por nivel, 792 series verificadas, nulos y excepciones,
conteos, segunda ejecución idempotente y recuperación de un fallo inducido en
una base de prueba. Los CSV originales completos permanecen fuera de Git.
