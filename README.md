# México · Laboratorio de inflación

Laboratorio interactivo para explorar la inflación en México con datos del INEGI,
series históricas y comparaciones regionales que ayudan a entender cómo cambian
los precios.

El proyecto incluye la base instalable de Python, el catálogo completo, el ETL
transaccional y PostgreSQL. La API y el dashboard se incorporarán mediante las
siguientes tareas del [plan de ejecución](docs/plan/README.md).

## Plan de desarrollo

La primera carga del ETL incorporará las 792 series del catálogo: México, las
32 entidades y 55 ciudades, con índice general y ocho rubros por ubicación.
La API y la interfaz se construirán por entregas sobre esa base completa.

El plan incluye arquitectura, contratos de datos y métricas, API, interfaz,
operación y 17 tareas con dependencias y criterios de aceptación. Para ejecutar
una tarea con otro modelo, usa el [prompt de trabajo](docs/plan/ejecucion.md) y
consulta el [seguimiento](docs/plan/seguimiento.md).

## Preparar el entorno

Instala [uv](https://docs.astral.sh/uv/getting-started/installation/) y Git. Desde
una rama de trabajo, ejecuta:

```bash
git switch -c feat/mi-cambio
make setup
```

`uv` prepara Python 3.12 y las dependencias de desarrollo fijadas en `uv.lock`.
`make setup` también instala el hook local de pre-commit. Cada clon necesita
ejecutar este paso.

## Verificar cambios

```bash
make check
make test
```

Se revisan formato, sintaxis de YAML/TOML/JSON, conflictos de merge, claves
privadas, archivos grandes y calidad de Python con Ruff. Algunos hooks corrigen
archivos; revisa los cambios y vuelve a ejecutar la verificación.

## Comandos disponibles

```bash
uv run inflacion-lab --help
uv run inflacion-lab --version
uv run python -m inflacion_lab --help
uv run inflacion-lab catalogo validar
uv run inflacion-lab etl run --mode bootstrap
```

Puedes copiar `.env.example` a `.env` para documentar la configuración local;
la ayuda y la importación del paquete no requieren secretos ni servicios
activos. `catalogo validar` comprueba offline las 88 geografías, nueve rubros y
792 series de `config/series.yml`. `etl run` descarga, valida y publica las 792
series como una única versión; si alguna falla, conserva la publicación previa.

## PostgreSQL de desarrollo

T03 incorpora PostgreSQL 18 en Compose. El puerto queda enlazado solamente a
`localhost` y el volumen `postgres_data` conserva los datos al recrear el
contenedor. Inícialo y crea una base de pruebas separada una sola vez:

```bash
make db-up
docker compose exec postgres createdb -U inflacion_lab inflacion_lab_test
export DATABASE_URL_MIGRATIONS=postgresql+psycopg://inflacion_lab:inflacion_lab@localhost:5432/inflacion_lab
export TEST_DATABASE_URL=postgresql+psycopg://inflacion_lab:inflacion_lab@localhost:5432/inflacion_lab_test
make db-migrate
make test-db
```

`make test-db` no crea ni deriva una URL desde la base de desarrollo: requiere
`TEST_DATABASE_URL` y rechaza cualquier nombre que no termine en `_test` antes
de ejecutar DDL. Para registrar el catálogo ya migrado de manera repetible usa:

```bash
uv run inflacion-lab catalogo registrar
```

Después de migrar la base de desarrollo y definir `DATABASE_URL_ETL`, ejecuta
la carga completa o sus actualizaciones:

```bash
make etl-bootstrap
make etl-refresh
make etl-reconcile
```

`refresh` exige un bootstrap exitoso y obtiene los últimos 24 meses; `reconcile`
vuelve a solicitar la historia desde 2018. Los originales y manifiestos se
guardan bajo `data/raw/` y no se versionan.

El comando usa `DATABASE_URL_MIGRATIONS`; repetirlo conserva 88 geografías,
nueve rubros y 792 series sin duplicarlas.

## Colaboración

El flujo es `rama de trabajo → pull request → CI → squash merge`.
`main` requiere un pull request, el check `Calidad` y las conversaciones
resueltas. La revisión de otra persona es opcional, por lo que puedes integrar
tus propios pull requests. Las reglas también aplican a administradores.

Consulta [CONTRIBUTING.md](CONTRIBUTING.md) para conocer los comandos, las reglas
de protección y su configuración en GitHub.

## Licencia

[MIT](LICENSE).
