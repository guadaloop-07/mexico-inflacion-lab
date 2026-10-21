# Contribuir

## Flujo de trabajo

1. Actualiza tu copia local de `main`:

   ```bash
   git switch main
   git pull --ff-only origin main
   ```

2. Crea una rama corta por cambio: `feat/`, `fix/`, `docs/` o `chore/`.

   ```bash
   git switch -c feat/mi-cambio
   make setup
   ```

3. Realiza el cambio y ejecuta `make check`. Agrega pruebas cuando el cambio lo
   requiera. Si un hook modifica archivos, revísalos y agrégalos de nuevo al
   siguiente commit.
4. Crea commits con mensajes descriptivos y publica tu rama:

   ```bash
   git add archivo-modificado
   git commit -m "feat: describe el cambio"
   git push -u origin feat/mi-cambio
   ```

5. Abre un pull request hacia `main`, explica el resultado y su validación.
6. Espera el check `Calidad` y resuelve las conversaciones de revisión que existan.
   Si `main` avanzó, actualiza tu rama y espera las verificaciones nuevamente.
   La revisión de otra persona es opcional; puedes integrar tus propios pull
   requests cuando cumplan las verificaciones.
7. Integra mediante squash merge. GitHub elimina la rama remota integrada.

## Hooks y CI

`make setup` sincroniza el entorno e instala pre-commit en el clon actual. Los
hooks locales bloquean commits sobre `main` y `master`; en las ramas de trabajo
revisan los archivos que se incluyen en cada commit.

`make check` ejecuta los checks sobre todos los archivos versionados. Usa la etapa
`manual`, por lo que puede ejecutarse sobre `main` o un checkout separado de CI.
La restricción de commits se ejecuta únicamente en la etapa `pre-commit`.

CI repite la verificación en cada pull request hacia `main` y después de integrar
cambios. El nombre `Calidad` es parte de la protección remota: actualiza también
esa configuración si renombras el job.

Los hooks locales se pueden omitir técnicamente; la protección en GitHub y CI son
los controles compartidos del equipo.

Las versiones resueltas están en `uv.lock`. Para actualizar las herramientas:

```bash
uv lock --upgrade
make setup
make check
```

Incluye el lockfile actualizado en el pull request. Las acciones de GitHub y los
hooks externos usan commits inmutables; Dependabot propone actualizaciones de
las acciones mediante pull requests.

## Protección de main

La configuración versionada establece:

- Pull request obligatorio, con cero aprobaciones externas requeridas.
- Check `Calidad` de GitHub Actions aprobado y rama actualizada respecto de `main`.
- Conversaciones de revisión resueltas e historial lineal.
- Protección para administradores; force push y eliminación de `main` bloqueados.
- Integración por squash y eliminación automática de ramas integradas.

Los JSON por sí solos no cambian GitHub. Una persona administradora puede aplicar
o restaurar la configuración desde la raíz del repositorio con GitHub CLI:

```bash
gh api --method PATCH repos/guadaloop-07/mexico-inflacion-lab \
  --input .github/repository-settings.json
gh api --method PUT repos/guadaloop-07/mexico-inflacion-lab/branches/main/protection \
  --input .github/main-protection.json
```

Puedes integrar tus propios pull requests una vez que se cumplan los checks y
las demás reglas de protección. La aprobación de otra persona es opcional.

## Archivos locales

Mantén credenciales en variables de entorno o archivos `.env` ignorados. Los
archivos `.env.example` pueden contener nombres de variables y valores ficticios.
Conserva descargas y resultados generados en `data/` o `artifacts/`, fuera de Git.
