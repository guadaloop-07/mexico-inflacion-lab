# Verificación y condiciones de entrega

## Principios

Las pruebas automáticas de PR no dependen del INEGI ni de credenciales reales.
Se usan originales pequeños atribuidos a la fuente y datos sintéticos explícitos
para casos límite. Las comprobaciones contra la fuente viva se registran aparte
y no sustituyen las pruebas repetibles.

Las pruebas de base se ejecutan en PostgreSQL 18 real, en una base cuyo nombre
termine en `_test`. `TEST_DATABASE_URL` es obligatorio para ellas. El fixture
de prueba rechaza bases ajenas a esa convención antes de crear, truncar o borrar.
No se utiliza SQLite para verificar transacciones, tipos ni upserts de Postgres.

## Matriz mínima

| Área | Casos que deben comprobarse |
|---|---|
| Catálogo | 88 geografías, 792 series, identidades únicas y nueve rubros por ubicación; IDs/etiquetas contrastados |
| HTTP | Timeout, 429 y reintento; error definitivo; HTML con HTTP 200; contenido incompleto |
| Parser | CSV real, columnas reordenadas, etiqueta desconocida/ambigua, meses en español, nulos, número inválido y duplicados |
| Cobertura | Falta una geografía o serie: no publicar; nulos legítimos preservados; mes interior ausente; archivo reciente con datos viejos |
| Escritura | Segundo lote idéntico sin duplicados; valor corregido con auditoría; fallo final revierte todo; exclusión de dos ETL simultáneos |
| Métricas | Mensual y anual por mes exacto; huecos; primer año sin denominador; negativa; cero de tasa válido; rango filtrado después de calcular |
| API | Validación, selección múltiple, límites, vacío, nulos, JSON/CSV equivalentes, ETag y 304 |
| Web | Filtros y URL, descarte de respuestas antiguas, estados y formato, comparación simultánea, calculadora |
| Integral | Fuente fixture → carga → API → navegador → CSV; fallo de refresh conserva versión válida |
| Operación | Backup y restore separados, reinicio de servicios, migración previa y rollback de aplicación |

Para fórmulas se usa además una tabla sintética de índices como 100 y 110, con
resultados calculados independientemente de la consulta SQL. Los fixtures
sintéticos se identifican como tales y nunca se usan como fallback público.

## CI y comandos

El check obligatorio sigue llamándose **Calidad** durante todas las tareas.
Cuando se agreguen jobs, ese check debe depender de ellos y fallar si cualquier
verificación requerida falla o se omite. La alternativa inicial más sencilla es
mantener los pasos en ese mismo job. No usar filtros de rutas que dejen el check
obligatorio permanentemente pendiente o hagan pasar una suite que no se ejecutó.

Los siguientes comandos se incorporan en las tareas indicadas; no existen todos
al momento de redactar el plan:

| Comando | Introducido en | Propósito |
|---|---|---|
| `make check` | Ya existe | Hooks sobre todos los archivos; T08 incluye lint/formato web |
| `make test` | T01 | Tests unitarios sin red ni base |
| `make db-up`, `make db-migrate` | T03 | Postgres local y esquema |
| `make test-db` | T03 | Tests marcados `integration`, con base separada |
| `make etl-bootstrap` | T05 | Primera carga real de las 792 series |
| `make etl-refresh`, `make etl-reconcile` | T05 | Ventana reciente o historia completa, siempre 792 series |
| `make api` | T07 | API local |
| `make setup-web`, `make web` | T08 | Instalar dependencias web y abrir servidor de desarrollo |
| `make test-web`, `make build-web` | T08 | Componentes/tipos y compilación |
| `make test-e2e` | T14 | Navegador contra servicios locales de prueba |

`make test` corresponde a `pytest -m 'not integration'`. `make test-db` selecciona
la marca `integration`. El CI de T03 incluye servicio Postgres y ambas suites.
T08 prepara Node antes de los hooks web y añade `npm ci`, tipos, tests y build.
T14 añade Playwright con Chromium y servicios aislados, sin descargar del INEGI.

No se agrega una suite vacía presentada como validación de negocio. Las pruebas
crecen al incorporar el comportamiento correspondiente.

## Evidencias fuera del resultado automático

En `docs/evidencias/Txx.md` registrar, cuando la tarea lo pida:

- Fecha, commit, entorno y alcance concreto de la verificación.
- Consulta, serie y periodo usados; fuente primaria; resultado y tolerancia.
- Conteos y cobertura sin subir las descargas completas ni secretos.
- Prueba de fallo/recuperación o restauración, si aplica.
- Limitaciones: cosas no ejecutadas y motivo real.

Los reportes voluminosos y capturas se guardan en `artifacts/` o como artifacts
de CI; el documento contiene el resumen y referencias recuperables.

## Revisión independiente de las decisiones sensibles

Después de T02, T05 y T06 conviene revisar identidad/cobertura, atomicidad y
fórmulas con atención adicional, aunque la implementación la haga un modelo
pequeño. La aprobación externa en GitHub continúa siendo opcional.

Una revisión puede ser realizada por la propietaria o por otro modelo con un
prompt limitado a esos contratos y al diff. No requiere rehacer toda la
planeación ni constituye autorización para cambiar código o integrar el PR.

## Lanzamiento

T14 reúne la evidencia de producto; T15 demuestra restauración. T16 verifica
la URL real, HTTPS, filtros, exportación, datos, versión y ejecución programada.
El lanzamiento se declara completo después de esas comprobaciones y de resolver
los datos de infraestructura que dependen de la propietaria.
