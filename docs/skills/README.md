# Skills — blender-mcp-ultra

Recetas operativas para agentes, probadas E2E en Blender 5.1.

Nuevas familias: `physics.particles/soft_body/constraint`, `export.*` (game/web/print), `perf.*`, `collab.*` (locks por objeto, tareas, assets), `blueprint.*`, `plan.*`, `docs.*`, `vc.*`, `vlm.*` (feedback visual), `scene.list_scenes/copy_object_to`, `compositor.*`, `scene_utils.undo/redo/ray_pick`.

| Skill | Contenido |
|---|---|
| [modeling.md](modeling.md) | Edición por componentes, bmesh, anti-blockout, validación |
| [animation.md](animation.md) | Keyframes, drivers, constraints, shape keys, física |
| [render_transactions.md](render_transactions.md) | Iluminación, jobs de render, snapshots/restore, locks |
| [headless_ci.md](headless_ci.md) | Servidor sin GUI, CI, tabla de errores → remediación |

## Descubrimiento de tools en runtime

```
list_tools                      # 217 tools con schema de parámetros
scene.query {name_contains}     # el grep de la escena
```

Los errores de tools incluyen campo `hint` con la remediación sugerida.
