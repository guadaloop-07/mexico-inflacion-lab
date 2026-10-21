# Ejecución con un modelo de contexto reducido

## Forma de trabajo

El modelo recibe una tarea, los documentos que esa tarea lista y el estado real
del repositorio. Implementa, verifica y deja un PR. La propietaria puede integrar
su propio PR cuando pase `Calidad`; no necesita aprobación externa.

Usar una conversación nueva por tarea ayuda a mantener el contexto acotado. El
registro durable es el código, los contratos, el PR y [seguimiento](seguimiento.md).
No depender de que el modelo recuerde esta conversación.

## Prompt para copiar

Sustituir `T01` y la ruta por la tarea elegida:

```text
Implementa T01 de docs/plan/tareas/T01-base-python.md en este repositorio.

Lee AGENTS.md, docs/plan/ejecucion.md, la ficha de la tarea y los documentos que
esa ficha indique. Comprueba sus dependencias en main y el estado del worktree.
Trabaja en una rama nueva desde main actualizado y respeta los cambios existentes.

Implementa la tarea completa con sus criterios de aceptación y pruebas. Conserva
los contratos del plan; resuelve decisiones internas rutinarias sin pedirme
confirmación. Si la fuente real contradice un supuesto, registra evidencia y
corrige la parte afectada del contrato. No inventes datos ni declares pruebas
que no ejecutaste.

El ETL del producto carga las 792 series desde su primera entrega; las muestras
pequeñas son únicamente fixtures de prueba. Respeta el alcance de esta ficha.
No adelantes otras tareas ni despliegues en infraestructura externa salvo que
la ficha y mi petición lo incluyan y cuentes con el acceso necesario.

Ejecuta las verificaciones indicadas, actualiza docs/plan/seguimiento.md con la
evidencia real y abre un PR hacia main. No lo integres sin que te lo indique.
Termina con lo implementado, las pruebas ejecutadas, limitaciones y enlace al PR.
Si falta un dato o acceso imprescindible, avanza en lo independiente y explica
exactamente qué parte queda pendiente.
```

Para una tarea siguiente se cambia también el archivo, por ejemplo `T02` y
`docs/plan/tareas/T02-catalogo-fuente.md`.

## Rutina de cada tarea

1. Comprobar el worktree y leer `AGENTS.md`. No mezclar cambios de la propietaria.
2. Actualizar referencias y comprobar que las dependencias están integradas.
   Un PR abierto todavía no cumple ese requisito. Consultar los enlaces del
   seguimiento y el código; no confiar solamente en una casilla marcada.
3. Crear `feat/tXX-descripcion`, `fix/...` o `docs/...` desde `main` actualizado.
4. Leer la ficha y las secciones pertinentes de los contratos. Evitar cargar
   indiscriminadamente todos los repositorios de referencia.
5. Implementar y probar comportamientos; agregar dependencias cuando se usan y
   actualizar el lockfile. Los comandos previstos se crean en su tarea, no se
   reportan como existentes antes de implementarlos.
6. Ejecutar `make check` y verificaciones de la ficha. La ausencia de red o
   Docker es una limitación del entorno; se informa qué prueba no pudo correr.
7. Actualizar seguimiento y las evidencias solicitadas; publicar el PR y revisar
   el resultado de CI. Corregir los fallos atribuibles al cambio.
8. Entregar el PR para integración por la propietaria. Después de integrar,
   verificar el estado y elegir la tarea siguiente.

## Tamaño y finalización

Cada ficha describe un resultado verificable y puede requerir más de un commit.
Si resulta demasiado grande, se divide en sub-PRs documentados sin relajar su
criterio de aceptación. En T05 esa división no permite declarar D1 con una carga
parcial: su último PR tiene que publicar las 792 series.

El modelo no agrega servicios, bibliotecas de infraestructura ni abstracciones
genéricas solo porque podrían servir después. Debe poder explicar qué criterio
de la tarea satisface cada cambio relevante.

Una tarea pasa a `PR abierto` con verificaciones registradas, y a `integrada`
cuando se confirma su merge. En el PR de la tarea siguiente se puede actualizar
el estado del anterior para no crear un PR separado solo por esa casilla.
`Bloqueada` se usa como estado de planificación cuando un requisito externo
impide terminar; se anota la dependencia precisa, sin sustituirla por un ejemplo.

## Revisión focalizada

Después de T02, T05 y T06, o si aparece una discrepancia económica, es útil una
revisión de mayor profundidad. Prompt de revisión, separado del implementador:

```text
Revisa el PR <URL> contra su ficha de tarea y los contratos de datos y API.
Prioriza identidad de series, cobertura, atomicidad, fechas y denominadores.
Indica defectos concretos con archivo/línea, impacto y evidencia. Distingue
defectos confirmados de verificaciones pendientes. No modifiques ni integres
el PR: esta petición es de revisión.
```

No hace falta usar el modelo de planificación para cada cambio mecánico. Conviene
reservar atención adicional para decisiones que puedan publicar cifras erróneas
o perder datos. La aprobación externa sigue siendo opcional en GitHub.
