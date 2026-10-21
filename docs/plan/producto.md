# Producto y alcance

## Público y propósito

Una persona sin formación económica debe poder consultar cómo cambian los
precios, comparar la inflación de su ubicación con México y explorar rubros.
La experiencia es pública, en español y usable desde un teléfono.

## Preguntas del primer lanzamiento

| Pregunta | Evidencia y vista |
|---|---|
| ¿Cuánto cambiaron los precios respecto al año pasado y al mes anterior? | Resumen con tasas anual y mensual, con mes visible |
| ¿Cómo ha evolucionado la inflación? | Serie histórica con medida y periodo explícitos |
| ¿Cómo se compara mi estado o ciudad con México? | Historias comparables y valores del mismo mes |
| ¿Qué rubros subieron más? | Barras de variación de los ocho rubros; no se presentan como contribuciones |
| ¿A cuánto equivale hoy una cantidad de otro mes? | Calculadora de monto actualizado por la razón entre índices |
| ¿Puedo revisar o reutilizar los datos? | CSV de la selección, fuente y explicación de medidas |

## Cobertura obligatoria del ETL desde su primera entrega

- Las 792 series del catálogo de referencia, sujetas a su verificación en T02.
- Las 88 ubicaciones: una nacional, 32 entidades y 55 ciudades del INPC.
- Periodicidad mensual. Historia desde enero de 2018 hasta el último mes cerrado
  que realmente haya publicado la fuente para cada serie.
- Índice general y ocho rubros por ubicación. Se conservan sus nombres oficiales.
- Nulos y diferencias legítimas de cobertura histórica visibles en los metadatos.

El catálogo y los parsers se prueban con muestras pequeñas, pero ningún bootstrap
de producto se considera exitoso si solo procesa esas muestras. D1 exige la
cobertura completa; no existe un modo de publicación parcial de una sola serie.

## Alcance de la primera versión pública

Una página de exploración, una calculadora y un apartado accesible de fuentes y
definiciones. Selección geográfica, mensual/anual, mes de corte e historia.
Comparación simultánea de hasta cuatro ubicaciones. CSV y enlaces compartibles
con la selección en parámetros de URL.

La API pública es de lectura y alimenta esta web. Se publica un contrato OpenAPI
y se limita el volumen de consultas. El ETL se ejecuta independientemente de las
visitas al sitio.

## Evolución posterior al lanzamiento

Se evaluarán después: datos quincenales, subyacente/no subyacente, genéricos,
incidencias oficiales, mapas y canastas personales. Cada ampliación necesita
fuente, definición y cobertura propias. Las ocho divisiones actuales no permiten
reconstruir por sí solas esas medidas.

El primer lanzamiento no necesita cuentas de usuario, pronósticos, procesamiento
en tiempo real ni personalización persistente.

## Condiciones de aceptación del producto

1. La primera carga publicada cubre las 792 series verificadas y deja evidencia
   de los nulos legítimos. Las diferencias de catálogo se resuelven antes de D1.
2. Los índices y variaciones coinciden con una muestra independiente de la fuente
   dentro de su precisión publicada; se registran serie, mes y tolerancia.
3. Cada vista permite recuperar periodo, unidad, geografía, fuente y estado de
   actualización. Una ejecución reciente no disfraza un periodo de datos viejo.
4. Los valores faltantes no aparecen como cero. Las comparaciones no mezclan
   meses distintos ni se presentan como diferencias de costo de vida.
5. La selección y el CSV representan la misma población y medida.
6. Es posible completar las preguntas principales en anchos de 360 y 1280 px,
   con teclado y sin depender exclusivamente del color.
7. Se demuestra actualización repetida, recuperación de un fallo, respaldo y
   restauración en una base separada antes del despliegue público.

En T14 se propone probar las preguntas principales con tres personas con poca
experiencia. Es una validación cualitativa de usabilidad, no una estimación
estadística. Si todavía no hay participantes, se registra esa limitación.
