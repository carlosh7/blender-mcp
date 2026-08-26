# v3.1.0 — "Spatial & Eyes + Agent Experience"

> Plan basado en (1) análisis de 24 MCPs de Blender en Glama, MCPs de Unity/
> Unreal/Houdini, y (2) **lecciones de una sesión real de construcción E2E**
> donde el agente usó el propio MCP para crear, romper y reparar escenas.

## 💎 Lecciones del agente (minadas de la sesión real)

| # | Problema vivido | Solución en v3.1.0 |
|---|---|---|
| 1 | Revertidos impredecibles: un error en `execute_blender_code` revirtió escenas enteras creadas (2×) | `txn_begin/commit/rollback` + `scene_diff` |
| 2 | Estado divergente silencioso: 3 escenas coexistiendo; el render usaba otra escena | Campo `scene` en toda respuesta que toca la escena |
| 3 | Colocar objetos: mesh offset del origen + escala heredada → `location` mentía | `place_bottom()` / `snap_to()` bbox-aware |
| 4 | Renderizar a ciegas: `scene.camera=None` con Camera existente; nunca supe qué veía la cámara | `camera_check()` (frustum vs objetos) + `render_preview()` |
| 5 | Física headless: RBW read-only, colección sin linkear, caché obsoleta | `physics_bake()` / `physics_free_cache()` |
| 6 | Basura de tests acumulada (RBC_*, SoftBody, escala ×2.2, `.001`) rompió renders | `scene_cleanup()` inteligente + auto-snapshot |
| 7 | Contexto: 429 objetos en un payload; 223 tools en schema | `tools_search()` + `get_scene_info(detail=)` |
| 8 | Protocolo: claves `type` vs `cmd_type` → "Unknown command: None" | Errores con contexto (escena + hint del schema) |

## Alcance

### H. Agent Experience (de las lecciones)
- `scene_diff(marker)` — objetos/transformas/materiales cambiados desde un marcador
- `place_bottom(name, x, y, z)` — coloca el bbox-min en el punto (no el origen)
- `snap_to(name, target, relation)` — on_top / beside / inside con colisión bbox
- `render_preview(samples, scale)` — draft EEVEE rápido para encuadre
- `camera_check()` — qué objetos están en el frustum + si la cámara está seteada
- `physics_bake(start, end)` / `physics_free_cache()` — primera clase
- `scene_cleanup(dry_run)` — duplicados `.001`, huérfanos, empties de test, escala no aplicada
- Enriquecimiento de errores: `scene` + `object_count` en toda respuesta de error

### C. Economía de contexto
- `tools_search(query, category)` — búsqueda sobre el registry
- `get_scene_info(detail="summary|full")` + paginación

### A. Inteligencia espacial
- `spatial_place(name, relation, target)` — above/below/beside/on + colisión
- `spatial_query(pattern, near, on)` — "¿qué hay sobre X?"
- `spatial_check_move(name, dx, dy, dz)` — distancia segura sin colisión
- `spatial_dimensions(category)` — DB de dimensiones reales (55+ objetos)
- `spatial_floorplan(views, cells)` — plano ASCII multi-vista
- `spatial_stack(names[])` — apilado estable

### B. Eyes (sin VLM)
- `inspect_view(name, mode)` — silhouette/wireframe/uv_checker/normales
- `inspect_turntable(name, frames)` — órbita
- `inspect_topology(name)` — ngons, UV stretch, densidad

### D/E/F. Explicación, transacciones, presets
- `scene_explain(target)` — objeto/material/nodo explicado en NL estructurado
- `txn_begin/commit/rollback` — transacciones explícitas
- `scene_preset(name)` / `scene_mood(mood)` — 10 presets + 6 moods

### G. Docs
- `docs/skills/scene-building-guide.md` — guía para agentes

## Fuera de alcance (v3.2+)
- Multi-instancia routing (Unity-style), runtime MCP (play mode), consentimiento por tool
