# México · Laboratorio de inflación

Laboratorio interactivo para explorar la inflación en México con datos del INEGI,
series históricas y comparaciones regionales que ayudan a entender cómo cambian
los precios.

El proyecto está en su etapa inicial. Este repositorio contiene la configuración
de colaboración y calidad; el ETL, la API y el dashboard se incorporarán en
cambios posteriores.

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
```

Se revisan formato, sintaxis de YAML/TOML/JSON, conflictos de merge, claves
privadas, archivos grandes y calidad de Python con Ruff. Algunos hooks corrigen
archivos; revisa los cambios y vuelve a ejecutar la verificación.

## Colaboración

El flujo es `rama de trabajo → pull request → CI → squash merge`.
`main` requiere un pull request, el check `Calidad` y las conversaciones
resueltas. La revisión de otra persona es opcional, por lo que puedes integrar
tus propios pull requests. Las reglas también aplican a administradores.

Consulta [CONTRIBUTING.md](CONTRIBUTING.md) para conocer los comandos, las reglas
de protección y su configuración en GitHub.

## Licencia

[MIT](LICENSE).
