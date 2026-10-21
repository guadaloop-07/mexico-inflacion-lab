# Métricas y contrato de API v1

## Cálculos canónicos

`I(s, t)` es el índice publicado de la misma serie `s` en el mes exacto `t`.
Se utilizan las series enlazadas oficiales, con su referencia documentada.

| Medida | Cálculo | Unidad y presentación |
|---|---|---|
| `indice` | `I(s, t)` | Puntos del índice; precisión de fuente |
| `mensual` | `100 × (I(s,t) / I(s,t-1 mes) - 1)` | Porcentaje; dos decimales en la web |
| `anual` | `100 × (I(s,t) / I(s,t-12 meses) - 1)` | Porcentaje; dos decimales en la web |
| Entre dos meses | `100 × (I(s,fin) / I(s,inicio) - 1)` | Porcentaje acumulado del intervalo |
| Monto actualizado | `monto × I(s,fin) / I(s,inicio)` | Pesos equivalentes; dos decimales en la web |
| Diferencia de tasas | `tasa_a - tasa_b` | Puntos porcentuales, no porcentaje |

Reglas comunes:

- Comparar por fecha exacta. Un `LAG(12)` sobre filas con huecos no garantiza el
  mismo mes del año anterior. Las consultas hacen joins por mes calendario.
- Calcular las tasas antes de recortar el rango de visualización. Pedir una
  historia de doce meses no elimina sus denominadores anteriores.
- Si un índice necesario es nulo o no existe, el resultado es `null` con su
  motivo. La inflación negativa es válida. Un denominador cero es un error de
  calidad del índice, no una tasa de cero.
- No sumar tasas mensuales; no promediar índices geográficos para fabricar el
  nacional. La inflación anual no se interpreta como promedio del año.
- No calcular incidencias ni explicar causas con este desglose. La comparación
  de tasas entre ciudades tampoco mide cuál ciudad tiene precios más altos.
- SQL conserva aritmética decimal; la conversión a números JSON ocurre en la
  frontera de API. Las tasas y montos se envían con hasta seis decimales; solo
  la presentación redondea a dos. CSV usa la misma precisión de la API.

Estas fórmulas y sus consultas viven en `db/metricas.py` y vistas versionadas
según corresponda. La calculadora reutiliza la razón entre índices del backend.
No se implementa una segunda versión de las fórmulas en TypeScript.

## Parámetros comunes

Base configurable: `/api/inflacion/v1`. API pública, lectura mediante GET.

| Parámetro | Dominio |
|---|---|
| `geografia` | ID de catálogo: `mx`, `entidad-14`, `ciudad-21`, etc. |
| `rubro` | Uno de los nueve IDs de [datos.md](datos.md) |
| `periodo` | `YYYY-MM`; por defecto el último mes con índice general no nulo de la geografía solicitada |
| `desde`, `hasta` | Meses `YYYY-MM`, ambos inclusivos; rango de historia |
| `medida` | `indice`, `mensual` o `anual`; por defecto `anual` |

La API valida fechas, orden de intervalos, precisión de montos y tamaño de las
selecciones. El máximo por petición es 240 meses, cuatro geografías y nueve
rubros. Estos límites cubren el historial inicial y se pueden aumentar con una
decisión documentada si la cobertura futura lo requiere.

Para selecciones múltiples se repite la clave:
`?geografia=mx&geografia=entidad-14`. Los duplicados se eliminan conservando el
orden. La selección de un mes futuro se rechaza como error de parámetros.

Para `/series`, `hasta` predetermina al último mes con general no nulo de la
geografía; `desde`, al mayor entre enero de 2018 y `hasta - 59 meses`.
`/comparacion` requiere un `periodo` explícito para el corte común; si también
se especifica `hasta`, debe coincidir con ese corte. Su inicio predeterminado
sigue la misma regla de cinco años. `/exportacion.csv` requiere rango y medida
explícitos. Si no hay publicación, no se inventan fechas predeterminadas.

## Rutas

| Ruta GET | Entrada | Resultado |
|---|---|---|
| `/catalogo` | Sin selección | Geografías, rubros, cobertura por serie y metadatos |
| `/resumen` | Una geografía y periodo opcional | General: índice, mensual, anual y motivos de nulos |
| `/series` | Una geografía, un rubro, medida y rango | Historia mensual ordenada, incluyendo huecos explícitos |
| `/comparacion` | Hasta cuatro geografías, un rubro, medida, rango y periodo de corte | Historias y valores del mismo corte, incluyendo participantes sin dato |
| `/rubros` | Una geografía, periodo y medida `mensual` o `anual` | Ocho rubros con sus tasas y estado; excluye general |
| `/calculadora` | Una geografía, `inicio`, `fin` y `monto` | General: índices, razón, variación acumulada y monto actualizado |
| `/exportacion.csv` | Geografías/rubros, medida y rango explícitos | CSV de esa misma consulta, con fuente y versión |
| `/health/live` | Sin parámetros | Proceso activo, sin consultar INEGI |
| `/health/ready` | Sin parámetros | Base accesible y esquema compatible |

Las rutas de negocio comparten el sobre descrito abajo. Salud y CSV usan los
formatos indicados por su tipo. OpenAPI documenta parámetros, ejemplos, límites,
errores y el carácter ilustrativo de los ejemplos numéricos.

La falta de una carga inicial no convierte al proceso en inaccesible: las rutas
de negocio responden vacío con `estado=sin_publicacion`. Readiness verifica el
esquema y acceso a la base; un fallo de esos requisitos devuelve 503.

## Forma de `datos` por ruta

Se mantienen estos nombres para que backend y frontend se puedan implementar
en PRs distintos sin reinterpretar el contrato:

| Ruta | Forma y campos |
|---|---|
| `/catalogo` | Objeto `geografias`, `rubros`, `series`; cada geografía tiene `id`, `nivel`, `nombre`; cada rubro `id`, `nombre`, `orden`; cada serie `geografia`, `rubro`, ID de fuente, base y límites de cobertura |
| `/resumen` | Objeto `periodo`, `indice`, `mensual`, `anual`; cada medida es `{valor, estado, unidad}` |
| `/series` | Lista de `{periodo, valor, estado}`; selección en `meta` |
| `/comparacion` | Objeto `historia` y `corte`, ambas listas de `{geografia, rubro, periodo, valor, estado}` |
| `/rubros` | Lista de `{rubro, nombre, periodo, valor, estado}` |
| `/calculadora` | Objeto `geografia`, `inicio`, `fin`, `monto_original`, `indice_inicio`, `indice_fin`, `razon`, `variacion_acumulada`, `monto_actualizado`, `estado` |

En `/catalogo`, los campos de fuente de una serie se llaman `id_serie_inegi`,
`base`, `periodo_min` y `periodo_max`; la metadata completa puede ampliarse con
campos aditivos documentados. `meta` incluye `version_datos`, fuente y frescura
también para el catálogo. Los identificadores internos de Postgres no forman
parte de la identidad pública.

Cuando una respuesta tiene unidades diferentes, como `/resumen`, las unidades
se indican por medida y `meta.unidad` es nulo. Los importes de calculadora usan
`pesos`; el índice usa `puntos_indice`, las tasas `porcentaje` y la razón es
adimensional. Sin una publicación inicial se devuelve la forma vacía pertinente
con `meta.estado=sin_publicacion`; para una selección válida sin observaciones,
`meta.estado=sin_datos`. Las demás respuestas usan `meta.estado=disponible`,
aunque una medida derivada tenga nulos por falta de denominador.

## Sobre de respuesta

Ejemplo de estructura **ilustrativa** de `/series`; los números no representan
observaciones oficiales ni deben utilizarse como datos de producción:

```json
{
  "datos": [
    {"periodo": "2020-01", "valor": 4.0, "estado": "disponible"},
    {"periodo": "2020-02", "valor": null, "estado": "sin_denominador"}
  ],
  "meta": {
    "estado": "disponible",
    "geografia": "mx",
    "rubro": "general",
    "medida": "anual",
    "unidad": "porcentaje",
    "desde": "2020-01",
    "hasta": "2020-02",
    "version_datos": "00000000-0000-0000-0000-000000000001",
    "ultima_carga_exitosa": "2020-03-10T16:00:00Z",
    "periodo_fuente_max": "2020-02",
    "fuente": "INEGI",
    "fuente_url": "https://www.inegi.org.mx/temas/inpc/"
  }
}
```

Estados de un valor: `disponible`, `no_publicado`, `sin_valor_fuente` y
`sin_denominador`. El primero tiene número; los demás tienen `null`. Un 0.00
medido sigue siendo `disponible`. Cuando falta la observación actual, su motivo
prevalece sobre el de un denominador anterior.

Cada respuesta añade la cobertura pertinente, con los límites observados por
serie. Las rutas múltiples identifican geografía/rubro en cada elemento y en
`meta.seleccion`; no afirman un único valor para selecciones heterogéneas.
`periodo_fuente_max` se refiere a la selección y conserva sus diferencias por
serie cuando existan. No equivale a la hora de descarga.

`/resumen` devuelve las medidas de general; `/rubros`, las tasas de los otros
ocho rubros para el mismo mes consultado. En ambas rutas,
`meta.periodo_consulta` explicita el corte.
El cambio de un control no dispara una sustitución silenciosa por otro mes.

## Comparaciones

El cliente envía un corte común a todas las geografías. Si una no tiene dato,
se conserva con nulo; no se usa su último mes por separado. Los límites de
historia y la medida son iguales para todas las líneas.

El historial devuelve una rejilla de meses y participantes, incluso si una
serie tiene huecos. Al dibujar, no se conectan puntos a través de esos huecos.
Una selección de un solo participante es válida; cuatro es el máximo inicial.

## Calculadora

Usa el índice general oficial de la geografía elegida. `monto` es decimal,
mayor que cero, con máximo dos decimales y límite de 1,000,000,000 pesos.
`inicio <= fin`; el mismo mes devuelve razón 1 y el mismo monto.

La respuesta contiene monto original, índices inicial/final, razón, porcentaje
acumulado y monto actualizado. La etiqueta explica: cantidad necesaria en el mes
final para conservar el poder de compra aproximado de la cantidad inicial según
ese índice. Es una actualización por INPC, no una canasta personal.

Un índice faltante produce resultado nulo con motivo, nunca una aproximación
automática. La validación de montos y fechas se repite en servidor.

## Exportación

UTF-8 y `text/csv`; encabezado estable:

```text
geografia_id,geografia,rubro_id,rubro,periodo,medida,valor,estado,version_datos,fuente_url
```

`valor` vacío representa nulo y se explica en `estado`. Orden: geografía, rubro,
periodo. La consulta reutiliza el servicio de métricas de las rutas JSON.
`Content-Disposition` proporciona un nombre sin caracteres introducidos por el
usuario. El botón de descarga utiliza explícitamente los filtros de su gráfica.

## Errores, coherencia y caché

- 404: geografía o rubro desconocidos.
- 422: fecha, monto, combinación de parámetros o límite inválidos.
- 200 con vacío/nulos: parámetros válidos sin observaciones disponibles.
- 503: base/esquema no disponibles. 500: fallo inesperado sanitizado.
- Los errores devuelven `codigo`, mensaje legible y detalles de campos cuando
  aplican; no contraseñas, trazas SQL ni rutas locales.
- Una respuesta lee datos y metadatos con `REPEATABLE READ` y solo lectura.
  `version_datos` permite comprobarlo entre componentes. Si cambia durante una
  actualización de pantalla, el cliente refresca el conjunto una vez; no mezcla
  versiones indefinidamente ni entra en bucle.
- Cache-Control público con una vida corta inicial de 300 segundos y ETag que
  incluya versión y parámetros normalizados. Manejar `If-None-Match` y 304.
  Salud y errores de infraestructura no se cachean como resultados válidos.
- Mismo origen para web y API. En desarrollo se usa proxy de Vite. La API no
  recibe un CORS abierto ni permite consultas SQL suministradas por el usuario.
