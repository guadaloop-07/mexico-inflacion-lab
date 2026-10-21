# Instrucciones del repositorio

- Trabaja en una rama `feat/`, `fix/`, `docs/` o `chore/`; conserva `main` como rama
  de integración mediante pull requests.
- Respeta la aprobación de otra persona, el check `Calidad` y las conversaciones
  resueltas. Conserva la protección de administradores, force push y borrado.
- Integra por squash únicamente cuando la tarea incluya autorización para integrar.
- Usa `uv` y conserva `uv.lock` al cambiar dependencias. Ejecuta `make setup` en un
  clon nuevo y `make check` antes de entregar cambios.
- Incorpora pruebas proporcionales al comportamiento que cambies. El repositorio
  todavía no tiene lógica de aplicación; agrega su verificación a CI al crearla.
- Conserva credenciales, descargas y archivos generados fuera de Git. Usa `data/`
  y `artifacts/` para resultados locales.
- Mantén las instrucciones de colaboración en `CONTRIBUTING.md` y verifica en
  GitHub las reglas remotas antes de afirmar que están activas.
