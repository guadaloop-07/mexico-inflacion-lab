# Instrucciones del repositorio

- Trabaja en una rama `feat/`, `fix/`, `docs/` o `chore/`; conserva `main` como rama
  de integración mediante pull requests.
- Respeta los pull requests, el check `Calidad` y las conversaciones resueltas.
  La revisión de otra persona es opcional. Conserva la protección de
  administradores, force push y borrado.
- Integra por squash únicamente cuando la tarea incluya autorización para integrar.
- Usa `uv` y conserva `uv.lock` al cambiar dependencias. Ejecuta `make setup` en un
  clon nuevo y `make check` antes de entregar cambios.
- Incorpora pruebas proporcionales al comportamiento que cambies. El repositorio
  todavía no tiene lógica de aplicación; agrega su verificación a CI al crearla.
- Conserva credenciales, descargas y archivos generados fuera de Git. Usa `data/`
  y `artifacts/` para resultados locales.
- Mantén las instrucciones de colaboración en `CONTRIBUTING.md` y verifica en
  GitHub las reglas remotas antes de afirmar que están activas.
- Para trabajo de aplicación, usa `docs/plan/README.md`, la ficha de la tarea y
  sus contratos. El primer ETL publica las 792 series: las muestras pequeñas
  son únicamente de prueba, no una reducción de cobertura del producto.
- Mantén `docs/plan/seguimiento.md` con evidencias reales y dependencias
  integradas. Una tarea de planeación no autoriza implementar otras fichas.
