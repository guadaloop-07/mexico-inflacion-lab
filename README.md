# México · Laboratorio de inflación

Laboratorio interactivo para explorar la inflación en México con datos del INEGI,
series históricas y comparaciones regionales que ayudan a entender cómo cambian
los precios.

El proyecto está en su etapa inicial. El repositorio incluye la base instalable
de Python, la configuración de colaboración y calidad y el
[plan de ejecución](docs/plan/README.md). El ETL, la API y el dashboard se
incorporarán mediante las tareas de ese plan.

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
```

La CLI todavía no descarga datos ni se conecta a una base. Puedes copiar
`.env.example` a `.env` para documentar la configuración local; la ayuda y la
importación del paquete no requieren secretos ni servicios activos.

## Colaboración

El flujo es `rama de trabajo → pull request → CI → squash merge`.
`main` requiere un pull request, el check `Calidad` y las conversaciones
resueltas. La revisión de otra persona es opcional, por lo que puedes integrar
tus propios pull requests. Las reglas también aplican a administradores.

Consulta [CONTRIBUTING.md](CONTRIBUTING.md) para conocer los comandos, las reglas
de protección y su configuración en GitHub.

## Licencia

[MIT](LICENSE).
