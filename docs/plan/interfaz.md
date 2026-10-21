# Interfaz y lenguaje

## Primera vista útil

Una página con título breve, fecha de los datos y controles. La vista inicial
usa México, medida anual, último mes con índice general disponible e historia
de cinco años o todo lo disponible si es menor. Si no hay publicación, presenta
un estado vacío explícito, sin cifras de ejemplo.

Orden de lectura del lanzamiento:

1. Ubicación y mes de corte; resumen con inflación anual y mensual.
2. Evolución histórica, con mensual/anual; el nivel del índice queda como opción
   de exploración adicional, con su referencia explicada.
3. Comparación con México y hasta otras ubicaciones seleccionadas.
4. Variación de los ocho rubros para el mismo mes y medida.
5. Calculadora de monto actualizado, con controles de fechas propios.
6. Fuentes, definiciones y descarga de la selección de cada vista.

T08 entrega los puntos 1–2 para México sobre la carga completa. T10 habilita
exploración de las 88 geografías y los puntos 3–4. T11 agrega la calculadora.

## Controles y alcance

| Control | Afecta |
|---|---|
| Geografía principal | Resumen, historia, rubros y geografía inicial de calculadora |
| Mes de corte | Resumen, final de historia, comparación y rubros |
| Medida mensual/anual | Historia, comparación y rubros; resumen conserva ambas |
| Inicio de historia | Solo historia y comparación; no cambia el mes del resumen |
| Geografías a comparar | Solo comparación; mismo mes, rango y medida |
| Monto, inicio y fin de calculadora | Solo calculadora; cambios no alteran el resto de la página |

Los filtros se inicializan desde parámetros de URL validados. Solo se comparten
geografías, medidas y periodos; el monto de la calculadora queda en memoria y no
se añade a la URL. Una selección inválida muestra un mensaje y permite regresar
a una selección válida. No se reinician todos los controles por una respuesta
lenta. Se cancelan o descartan peticiones antiguas al cambiar de selección.

La comparación inicial agrega México y la geografía elegida si son distintas.
Si se elige México, el control permite agregar una entidad o ciudad sin fingir
una comparación duplicada. Las ciudades pertenecen al catálogo INPC y no se
identifican como municipios.

## Gráficas

- Historia: líneas, ejes legibles, unidad visible y tooltip de mes/valor.
  Huecos como huecos; marcas distinguibles también por patrón o estilo.
- Comparación: líneas simultáneas con misma escala y leyenda estable. Se limita
  a cuatro para mantener legibilidad. El último valor de cada participante
  corresponde al mes de corte común, o muestra sin dato.
- Rubros: barras horizontales, orden por tasa con desempate estable, referencia
  de cero visible y etiquetas completas o expandibles. Con inflación negativa
  se utiliza una escala que represente ambos signos.
- Valores exactos y alternativa tabular accesible junto a su gráfica. La tabla
  puede estar plegada; no necesita convertirse en una página separada.
- Una diferencia entre tasas se rotula en puntos porcentuales. No se asigna
  significado de bueno/malo a un color sin una definición del producto.

## Sistema visual inicial

Fondo claro, texto oscuro, un acento principal, dos niveles de superficies y
espaciado consistente. Tipografía del sistema inicialmente. CSS variables para
color, espaciado, radios y tamaños; sin imágenes decorativas necesarias.

En escritorio se agrupan controles y el resumen conserva su prominencia. En
móvil se apilan los bloques, se ajustan las etiquetas y las tablas anchas
desplazan dentro de su contenedor. No hay scroll horizontal de toda la página.
El contraste y el foco se verifican en T14; elegir un color no demuestra por sí
solo que cumple accesibilidad.

## Explicaciones que deben aparecer cerca de la medida

- Anual: cambio respecto al mismo mes del año anterior.
- Mensual: cambio respecto al mes anterior.
- Menor inflación positiva: los precios siguen aumentando, a menor ritmo.
- Índice: nivel relativo a su periodo de referencia, no un precio en pesos.
- Rubros: variaciones de cada grupo, no contribuciones al total.
- Geografía: diferencias de inflación no equivalen a diferencias del costo de
  vida entre ubicaciones.
- Calculadora: actualización por el índice elegido, no gasto personal observado.

Mantener los nombres completos de rubros disponibles. Las etiquetas abreviadas
de las referencias antiguas no sustituyen la definición oficial.

## Estados y procedencia

Distinguir carga inicial, actualización en curso, selección sin observaciones,
valor cero, nulo de fuente, denominador faltante y error de conexión. Un error
no se reemplaza por datos simulados. Si se conserva una vista anterior durante
una recarga, se indica que pertenece a la selección anterior.

Mostrar el periodo observado y la última carga exitosa como cosas distintas.
La fuente enlaza al INEGI; un apartado desplegable explica base, cobertura,
clasificación, fórmulas y limitaciones. Los textos dependen del contenido real
de `meta`, incluyendo los nulos iniciales de la inflación anual de 2018.

## Accesibilidad y revisión

Controles con etiquetas asociadas, foco visible, navegación por teclado,
encabezados semánticos y estados anunciados sin saturar el lector de pantalla.
Las descripciones de ECharts complementan la tabla; no la sustituyen.

Inspeccionar 360, 768 y 1280 px, navegación con teclado y descargas. Comprobar
que fuente, unidades, tooltips, tabla y CSV coinciden después de filtrar. Usar
fixtures reconocibles para estados de prueba; producción consulta la API real.
