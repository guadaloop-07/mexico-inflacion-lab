# Fuentes y verificaciones pendientes

Referencias consultadas el 20 de octubre de 2026. Este listado respalda las
decisiones técnicas; no afirma haber contrastado todos los valores del INPC.

## Datos y metodología

- [INEGI: INPC](https://www.inegi.org.mx/temas/inpc/): fuente oficial de consulta,
  resultados y metadatos.
- [INEGI: materiales metodológicos de la actualización 2024](https://www.inegi.org.mx/rnm/index.php/catalog/1015/related-materials):
  documentación de canasta, ponderadores y encadenamiento. Es una referencia
  histórica; T02 verificará qué versión corresponde a las series vigentes.
- Exportador observado en los extractores de referencia:
  `https://www.inegi.org.mx/app/indicesdepreciosv2/Exportacion.aspx`.
  Es parte de la aplicación del INEGI; su formato y parámetros necesitan prueba
  real. No se presupone un contrato estable ni se sustituye por datos de terceros.

## Referencias locales revisadas

- `~/inpc_inegi_extractor`: catálogo explícito y descarga XLS. Configura 792
  series desde 2018. Los archivos locales reutilizados no demuestran frescura.
- `~/iieg/ETL-SIEEJ/core/pipelines/inpc`: descarga CSV agrupada, catálogos y carga
  SQLAlchemy. Sus supuestos de orden de columnas y su filtro de fechas no son
  el contrato del nuevo producto.
- Se comprobó coincidencia de IDs generales para 32 estados y 55 ciudades entre
  esos catálogos. No se comprobó equivalencia de los nueve índices de todas las
  ubicaciones contra respuestas actuales de la fuente.

Estas rutas ayudan a T02, pero no son dependencias de runtime. Se documenta la
procedencia del catálogo incorporado y la atribución que corresponda al código
que efectivamente se reutilice.

## Documentación técnica primaria

| Referencia | Uso en el plan |
|---|---|
| [PostgreSQL: INSERT](https://www.postgresql.org/docs/current/sql-insert.html) | Upsert y restricciones para cargar sin duplicar |
| [PostgreSQL: SQL dump](https://www.postgresql.org/docs/current/backup-dump.html) | Respaldo lógico y restauración |
| [SQLAlchemy 2.1](https://docs.sqlalchemy.org/en/21/) | Tablas, conexiones y consultas Core |
| [Alembic](https://alembic.sqlalchemy.org/en/latest/tutorial.html) | Migraciones versionadas |
| [FastAPI](https://fastapi.tiangolo.com/) | API tipada y OpenAPI |
| [React: construcción con Vite](https://react.dev/learn/build-a-react-app-from-scratch) | Base frontend, apropiada para esta página de cliente |
| [Vite](https://vite.dev/guide/) | Desarrollo y build estático |
| [ECharts: accesibilidad](https://echarts.apache.org/handbook/en/best-practices/aria/) | Descripciones y alternativas accesibles |
| [Playwright en CI](https://playwright.dev/docs/ci) | Verificación integral en navegador |
| [Docker Compose en producción](https://docs.docker.com/compose/how-tos/production/) | Servicio en un servidor y configuración por entorno |
| [Imagen oficial de Postgres](https://github.com/docker-library/docs/blob/master/postgres/README.md) | Persistencia y particularidades de volúmenes en Postgres 18 |

Se consultarán las versiones estables compatibles de dependencias e imágenes al
introducirlas. El plan fija familias tecnológicas y contratos; los lockfiles e
imágenes fijadas identifican la implementación exacta.

## Evidencia que debe producir T02

- Respuestas CSV actuales de México, Jalisco y Guadalajara, con nueve índices,
  un intervalo suficiente para verificar tasas y sus metadatos de descarga.
- Vínculo explícito entre ID, etiqueta, frecuencia, clasificación y base.
- Comprobación del catálogo completo contra metadatos oficiales disponibles y
  registro de cualquier discrepancia. La prueba de tres ubicaciones no se
  describe como validación completa de valores de las 792 series.
- Codificación, delimitador, encabezados, marcadores de ausencia y estructura
  de fechas demostrados por los archivos, sin depender de posiciones supuestas.
- Referencia vigente del calendario de publicación. Si no se puede verificar,
  registrar esa limitación para T12 sin inventar fechas.

## Riesgos y respuesta

| Riesgo | Respuesta y tarea |
|---|---|
| Cambia el exportador | Fixtures reales y validación semántica; fallar conservando publicación anterior, T02/T04/T05 |
| Una serie está mal etiquetada | Catálogo trazable, comprobación de metadatos y rechazo de ambigüedad, T02/T04 |
| Una carga queda incompleta | Validación de las 792 series y transacción única, T05 |
| Una revisión histórica pasa inadvertida | Ventana reciente de 24 meses y reconciliación completa, T05/T12 |
| El visitante interpreta tasa como precio | Lenguaje junto a las vistas y prueba de uso, T10/T14 |
| Falta acceso al servidor | Completar preparación local; pedir únicamente los datos necesarios para T16 |
| El respaldo no recupera el sistema | Restauración aislada antes del lanzamiento, T15/T16 |
