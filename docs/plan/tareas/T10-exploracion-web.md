# T10 · Exploración de ubicaciones y rubros

Dependencias: T08, T09. Rama sugerida: `feat/t10-exploracion-web`.

## Objetivo

Habilitar las preguntas de comparación y rubros para todo el catálogo, con
controles comprensibles y resultados que se puedan compartir y descargar.

## Leer

`AGENTS.md`, `../ejecucion.md`, `../interfaz.md`, `../api.md` y
`../producto.md`.

## Implementar

- Selector de ubicación con nivel nacional/entidad/ciudad y búsqueda sencilla.
- Comparación simultánea de hasta cuatro ubicaciones, con la regla de selección
  inicial y los controles compartidos de mes/medida/rango del contrato.
- Barras de los ocho rubros, incluyendo negativos y estados sin dato.
- Enlaces con selección en URL; validación y regreso a selección válida.
- Descarga por vista que envía sus filtros exactos al endpoint CSV.
- Explicaciones breves de anual/mensual, índice, rubros y comparación geográfica.
- Tabla accesible y comportamiento móvil para cada nueva gráfica.

## Aceptación y comprobación

- Elegir Jalisco o Guadalajara actualiza resumen, historia y rubros de forma
  consistente. Elegir México no dibuja dos copias de la misma serie.
- La comparación muestra participantes juntos; un selector de uno en uno no
  sustituye esta vista. Máximo cuatro y misma escala/periodo.
- Enlaces recargados conservan filtros válidos. Las peticiones antiguas y errores
  no vuelven a etiquetar datos de una selección anterior.
- Tests de interacción verifican controles, URLs, estados y filtros de descarga.
- Inspección en 360, 768 y 1280 px y teclado; registrar evidencia en
  `docs/evidencias/T10.md`.
- `make check`, suites existentes, `make test-web`, `make build-web` y CI pasan.

No añadir mapas, causas automáticas ni comparaciones de niveles de precios entre
ciudades. La calculadora se incorpora en T11 sin un placeholder engañoso.
