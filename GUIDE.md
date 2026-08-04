# blender-mcp v0.8.0 — Guía Completa

> 82 tools · 4 resources · 3 prompts · 5 integraciones · 9 clientes

---

## 1. Arquitectura General

```
CUALQUIER CLIENTE MCP              SERVIDOR MCP                    BLENDER
(Claude, Cursor, opencode,  ──►   mcp_server.py  ──socket──►    addon/
 Antigravity, VS Code,             82 tools MCP     port 9876     ├─ handlers/ (22)
 Windsurf, LM Studio,              4 recursos                     ├─ blender_socket.py
 Ollama, Continue)                 3 prompts                      ├─ panels/
                                                                  ├─ operators/
                                                                  └─ client/ (embedded)
```

### Modos de operación

| Modo | Cómo funciona | Velocidad | Cuándo usarlo |
|------|--------------|-----------|---------------|
| **Proxy** | Claude/Cursor externo maneja el loop de IA | ⚡ Rápido | Cuando tienes Claude Desktop, Cursor, VS Code |
| **Autonomous** | El agente embebido llama al LLM directamente | 🐢 Lento | Cuando NO tienes Claude Desktop |
| **Local AI** | LLM dentro de Blender (Ollama, OpenAI, etc.) | 🐌 Variable | Sin internet, o quieres control total |

Para cambiar: Panel **Axiom → Integrations → Agent Mode**: Auto / Proxy / Autonomous

---

## 2. Instalación y Conexión

### 2.1 Activar el addon en Blender
1. Abre Blender → `Edit → Preferences → Add-ons`
2. Busca "AXIOM Precision Engine"
3. Actívalo (checkmark)
4. En el viewport 3D, presiona `N` → pestaña **Axiom**

### 2.2 Conectar
- **Con MCP externo**: Click `Connect` → se conecta al socket :9876
- **Con IA local**: Click `Local AI` → arranca servidor embebido :45677
- Server externo: `blender-mcp --mode stdio`

---

## 3. Panel de Blender (Axiom Tab)

### Chat (pestaña principal)
```
┌─────────────────────────────────┐
│ [Connect] [Local AI] [Disconnect] │  ← Estado de conexión
│ [Vision] [Export]               │  ← Acciones rápidas
│ ┌───────────────────────────┐   │
│ │ Chat history               │   │  ← Conversación con IA
│ │ ...                         │   │
│ └───────────────────────────┘   │
│ [Escribe tu mensaje...]         │  ← Input
│ [Send] [Clear]                  │
└─────────────────────────────────┘
```

### Integrations (pestaña secundaria)
Aquí activas cada servicio externo:

| Checkbox | Servicio | API Key | Gratis |
|----------|----------|---------|--------|
| Poly Haven | HDRI / Texturas / Modelos 3D | No | ✅ Sí |
| Sketchfab | Modelos realistas | Sí | ❌ |
| Hyper3D Rodin | Generación IA texto→3D | Sí (o Free Trial) | ⚠️ Limitado |
| Hunyuan3D | Generación IA texto/imagen→3D | Sí | ❌ |
| AmbientCG | Materiales PBR | No | ✅ Sí |

### Config (Properties panel)
- **Provider**: Selecciona el proveedor LLM (OpenAI, DeepSeek, Anthropic, etc.)
- **Model**: Modelo específico
- **Agent Mode**: Proxy / Auto / Autonomous

---

## 4. Guía Rápida de Tools (82)

### 4.1 Escena (Scene) — 10 tools

| Tool | Qué hace | Ejemplo |
|------|----------|---------|
| `get_scene_info()` | Info de toda la escena | objetos, nombres, tipos |
| `get_object_info(name)` | Info de un objeto específico | posición, rotación, escala, vértices |
| `execute_blender_code(code)` | Ejecuta Python en Blender | `bpy.ops.mesh.primitive_cube_add()` |
| `get_viewport_screenshot()` | Captura del viewport | Para validación visual |
| `get_viewport_screenshot_image()` | Captura como imagen MCP | Visible directamente por el LLM |
| `get_scene_visual()` | Vista ASCII cenital | Para razonamiento espacial |
| `search_assets()` | Busca en Poly Haven / Sketchfab | `search_assets("polyhaven", "brick", "textures")` |
| `generate_3d_model(prompt)` | Genera modelo 3D con IA | `generate_3d_model("un jarrón antiguo")` |
| `export_to_planner(name)` | Exporta a GLB para planner 3D | `export_to_planner("mi_mesa")` |
| `purge_orphans()` | Elimina datos huérfanos | Limpieza de escena |

### 4.2 Objetos (Objects) — 5 tools

| Tool | Qué hace |
|------|----------|
| `create_object(type, name, location)` | Crea cubo, esfera, cilindro, cono, toro, plano, mono |
| `delete_object(name)` | Elimina un objeto |
| `transform_object(name, location, rotation, scale)` | Mueve, rota, escala |
| `duplicate_object(name, new_name)` | Duplica un objeto |
| `select_object(name)` | Selecciona un objeto |

### 4.3 Materiales (Materials) — 5 tools

| Tool | Qué hace |
|------|----------|
| `create_material(name, color, roughness, metallic)` | Crea material PBR |
| `assign_material(object, material)` | Asigna material a objeto |
| `set_color(object, color)` | Color rápido |
| `list_materials()` | Lista todos los materiales |
| `set_shader_node_value(material, node, input, value)` | Ajusta valor de nodo |

### 4.4 Luces (Lights) — 2 tools

| Tool | Qué hace |
|------|----------|
| `create_light(name, type, energy, color, location)` | Point, Sun, Spot, Area |
| `setup_three_point_lighting(target)` | Iluminación profesional automática |

### 4.5 Cámara (Camera) — 3 tools

| Tool | Qué hace |
|------|----------|
| `create_camera(name, location, lens)` | Crea cámara con lente |
| `set_camera_target(camera, target)` | Apunta cámara a objeto |
| `auto_frame(target)` | Encuadra automáticamente |

### 4.6 Modificadores (Modifiers) — 4 tools

| Tool | Qué hace |
|------|----------|
| `add_modifier(object, type)` | SubSurf, Bevel, Boolean, Array, Mirror, Solidify... (22 tipos) |
| `remove_modifier(object, name)` | Elimina modificador |
| `list_modifiers(object)` | Lista modificadores |
| `apply_modifier(object, name)` | Aplica modificador |

### 4.7 Shader Nodes — 5 tools

| Tool | Qué hace |
|------|----------|
| `add_shader_node(material, type)` | Añade nodo (40+ tipos: bsdf_principled, emission, tex_image, etc.) |
| `connect_shader_nodes(material, from, to)` | Conecta dos nodos |
| `set_shader_node_value(material, node, input, value)` | Cambia valor |
| `list_shader_nodes(material)` | Lista árbol de nodos |
| `remove_shader_node(material, node)` | Elimina nodo |

### 4.8 Animación (Animation) — 5 tools

| Tool | Qué hace |
|------|----------|
| `insert_keyframe(object, frame, property)` | Keyframe en propiedad |
| `animate_location(object, start, end, from, to)` | Animación de posición |
| `animate_rotation(object, start, end, revolutions)` | Animación de rotación |
| `animate_scale(object, start, end, from, to)` | Animación de escala |
| `set_render_range(start, end)` | Rango de frames |

### 4.9 Geometry Nodes — 5 tools

| Tool | Qué hace |
|------|----------|
| `add_geometry_nodes_modifier(object)` | Añade modificador GN |
| `add_gn_node(object, type)` | Añade nodo al grupo |
| `connect_gn_nodes(object, from, to)` | Conecta nodos |
| `setup_gn_scatter(object, density)` | Sistema de scattering rápido |
| `list_gn_modifiers(object)` | Lista modifiers GN |

### 4.10 Render — 5 tools

| Tool | Qué hace |
|------|----------|
| `set_render_engine(engine)` | Cycles / EEVEE / Workbench |
| `set_render_resolution(w, h)` | Resolución de salida |
| `set_render_samples(samples)` | Muestras Cycles |
| `render_frame(filepath)` | Renderiza frame actual |
| `set_cycles_device(device)` | GPU / CPU |

### 4.11 Import/Export (IO) — 4 tools

| Tool | Formatos |
|------|----------|
| `export_scene(filepath, format)` | glb, gltf, fbx, obj, stl, ply, usd, dae, abc, x3d (12 formatos) |
| `export_selected(filepath, format)` | Exporta solo seleccionados |
| `import_model(filepath, format)` | Importa (13 formatos, auto-detecta extensión) |
| `list_export_formats()` | Lista formatos disponibles |

### 4.12 UV & Texture — 4 tools

| Tool | Qué hace |
|------|----------|
| `unwrap_object(object, method)` | Smart, Angle Based, Conformal, Cube, Cylinder, Sphere |
| `add_uv_map(object)` | Añade canal UV |
| `bake_textures(object, type)` | Bakea diffuse, normal, ao, roughness... |
| `list_uv_maps(object)` | Lista canales UV |

### 4.13 Batch — 4 tools

| Tool | Qué hace |
|------|----------|
| `turntable_render(object, frames)` | Render 360° automático |
| `batch_rename(prefix/search, replace)` | Renombrado masivo |
| `batch_delete_by_type(type)` | Elimina por tipo (MESH, LIGHT, etc.) |
| `apply_transforms_all()` | Aplica transforms a todos |

### 4.14 Rigging — 5 tools

| Tool | Qué hace |
|------|----------|
| `create_armature(name)` | Crea armadura con hueso |
| `add_bone(armature, name, head, tail)` | Añade hueso |
| `add_constraint(object, type, target)` | Copy Location, Track To, etc. |
| `parent_with_armature(object, armature)` | Parent con modifier Armature |
| `auto_rig_weight(object, armature)` | Weight paint automático |

### 4.15 Scene Utils — 6 tools

| Tool | Qué hace |
|------|----------|
| `purge_orphans()` | Purga datos huérfanos |
| `cleanup_scene()` | Limpieza completa + remover colecciones vacías |
| `mesh_analysis(object)` | Estadísticas de malla (vértices, caras, dimensiones) |
| `scene_summary()` | Resumen completo de la escena |
| `hide_object(name, hide)` | Oculta/muestra objeto |
| `join_objects(target, sources)` | Une objetos en una malla |

### 4.16 3D Printing — 5 tools

| Tool | Qué hace |
|------|----------|
| `check_manifold(object)` | Verifica si es watertight (manifold) |
| `set_dimensions_mm(w, d, h)` | Dimensiones exactas en milímetros |
| `export_stl_mm(filepath)` | Exporta STL con escala mm |
| `arrange_bed_layout(objects, w, h)` | Distribuye objetos en cama de impresión |
| `add_wall_thickness(object, mm)` | Añade grosor de pared (Solidify) |

### 4.17 Poly Haven — 6 tools

| Tool | Qué hace |
|------|----------|
| `get_polyhaven_status()` | Estado de la integración |
| `search_polyhaven(type, query)` | Busca HDRI, texturas o modelos |
| `get_polyhaven_categories(type)` | Categorías disponibles |
| `download_polyhaven_hdri(asset_id)` | Descarga y aplica HDRI como mundo |
| `download_polyhaven_texture(asset_id)` | Descarga textura PBR + crea material |
| `download_polyhaven_model(asset_id)` | Descarga e importa modelo 3D |

### 4.18 Sketchfab — 4 tools

| Tool | Qué hace |
|------|----------|
| `get_sketchfab_status()` | Estado de la integración |
| `search_sketchfab(query, count)` | Busca modelos |
| `get_sketchfab_preview(uid)` | Preview thumbnail |
| `download_sketchfab_model(uid, size)` | Descarga e importa modelo |

### 4.19 Hyper3D Rodin — 4 tools

| Tool | Qué hace |
|------|----------|
| `get_hyper3d_status()` | Estado de la integración |
| `generate_hyper3d_text(prompt)` | Genera 3D desde texto |
| `poll_rodin_job(key)` | Verifica estado de la generación |
| `import_rodin_asset(name, uuid)` | Importa el modelo generado |

### 4.20 Hunyuan3D — 4 tools

| Tool | Qué hace |
|------|----------|
| `get_hunyuan3d_status()` | Estado de la integración |
| `generate_hunyuan3d(text, image_url)` | Genera 3D desde texto o imagen |
| `poll_hunyuan_job(job_id)` | Verifica estado |
| `import_hunyuan_asset(name, zip_url)` | Importa modelo |

### 4.21 AmbientCG — 3 tools

| Tool | Qué hace |
|------|----------|
| `search_ambientcg(query)` | Busca materiales PBR (gratis) |
| `get_ambientcg_categories()` | Categorías disponibles |
| `download_ambientcg_material(asset_id)` | Descarga + crea material |

---

## 5. Recursos MCP

```
blender://scene/info           → Info general de la escena
blender://scene/objects         → Lista de objetos
blender://scene/materials       → Lista de materiales
blender://scene/active-object   → Objeto activo actual
```

## 6. Prompts MCP

| Prompt | Para qué sirve |
|--------|----------------|
| `asset_creation_strategy()` | Guía al LLM sobre qué integración usar primero |
| `scene_analysis_strategy()` | Cómo analizar y debuggear una escena |
| `geometry_nodes_documentation()` | Cómo documentar setups de Geometry Nodes |

---

## 7. Skills Claude Code (10 skills)

```bash
# Instalar
for skill in skills/*/; do
    ln -sfn "$PWD/$skill" "$HOME/.claude/skills/$(basename $skill)"
done
```

| Skill | Uso |
|-------|-----|
| `text-to-blender` | Entry point: "crea una espada y renderízala" |
| `blender-modeling` | Primitivas, modifiers, topología |
| `blender-materials` | Materiales PBR: metal, vidrio, madera |
| `blender-lighting` | Iluminación 3 puntos, HDRI |
| `blender-cameras` | Cámaras, lentes, DOF |
| `blender-rendering` | Cycles/EEVEE, resolución |
| `blender-animation` | Keyframes, rotación, escala |
| `blender-export` | GLB, FBX, OBJ, STL, USD |
| `wireframe-to-3d` | De wireframe 2D a modelo 3D |
| `blender-pro-workflow` | Pipeline profesional de 6 fases |

---

## 8. Flujo de Trabajo Típico

### Ejemplo 1: Crear escena desde Claude

```
User: "Crea una mesa redonda de 1.5m con 4 sillas, iluminación 3 puntos"
  ↓ Claude llama:
  1. get_scene_info() → ver escena
  2. create_object(type="CYLINDER", ...) → mesa
  3. create_object(type="CUBE", ...) × 4 → sillas
  4. create_material("wood", color=[0.55, 0.35, 0.15])
  5. assign_material("Mesa", "wood")
  6. setup_three_point_lighting()
  7. get_viewport_screenshot_image() → validar
```

### Ejemplo 2: Usar assets externos

```
User: "Busca una textura de ladrillo y aplícala al muro"
  ↓ Claude llama:
  1. search_polyhaven("textures", "brick") → encuentra asset
  2. download_polyhaven_texture("brick_wall_01", "2k")
  3. assign_material("Muro", "brick_wall_01")
```

### Ejemplo 3: Análisis de escena

```
User: "Analiza la escena y dime qué tiene más polígonos"
  ↓ Claude llama:
  1. get_scene_info()
  2. mesh_analysis("objeto_sospechoso")
  3. mesh_analysis("otro_objeto")
```

### Ejemplo 4: Exportar para impresión 3D

```
User: "Exporta esta pieza para impresión 3D en milímetros"
  ↓ Claude llama:
  1. check_manifold("Pieza")
  2. set_dimensions_mm("Pieza", width_mm=100, height_mm=50)
  3. add_wall_thickness("Pieza", thickness_mm=2)
  4. export_stl_mm("/ruta/pieza.stl")
```

---

## 9. Solución de Problemas

| Problema | Causa | Solución |
|----------|-------|----------|
| No conecta | Blender no tiene el addon activo | Activar AXIOM Precision Engine |
| Socket timeout | Blender ocupado | Simplificar request |
| Poly Haven no funciona | Checkbox desactivado | Activar en Integrations |
| Sketchfab no encuentra | API Key no configurada | Poner API Key en Integrations |
| Agente lento | Modo autónomo sin streaming | Usar modo Proxy (Claude Desktop) |
| Addon no aparece | Versión Blender | Blender 4.0+ mínimo |
| `blender-mcp: command not found` | uv no instalado | `curl -LsSf https://astral.sh/uv/install.sh | sh` |

---

## 10. v2.0 — Superficie completa (128 tools)

> Blender **4.2 LTS .. 5.x** · 114 comandos en `addon/handlers.py` · 128 tools MCP
> generadas desde una sola spec (`mcp_tools.py`) para FastMCP y `stdio_bridge.py`.

### Modelado (desde cero, background-safe)
`create_object` (CUBE/PLANE/SPHERE/UVSPHERE/ICOSPHERE/CYLINDER/CONE/TORUS/
MONKEY/GRID/CIRCLE/EMPTY), `transform_object`, `duplicate_object`,
`add_modifier` (18 tipos: subsurf, bevel, boolean, array, mirror, solidify,
screw, wireframe, decimate, remesh, weld, displace…), `boolean_operation`,
`bevel_mesh`, `extrude_face`, `inset_face`, `merge_by_distance`, `clean_mesh`,
`join_objects`, `create_text`, `create_curve`, `create_screw_profile` (torno),
`apply_transform`, `apply_modifiers` (bake), `create_empty`,
`subdivide_mesh`, `loop_cut` (bisect_plane).

### Coloreado / materiales
`create_material` (Principled BSDF: color, roughness, metallic, emission, IOR,
alpha, transmission), `assign_material`, `set_color`, `add_shader_node`
(26 tipos), `connect_shader_nodes`, `set_node_value`, `remove_shader_node`,
`create_image_texture`, `assign_image_texture`, `add_vertex_color`,
`set_emission`, `set_transparency`, `colorize_from_scratch`.

### Rigging
`create_armature`, `add_bone`, `remove_bone`, `list_bones`, `rename_bone`,
`add_vertex_group`, `assign_vertex_weights`, `remove_vertex_group`,
`add_constraint` (20 tipos), `setup_ik_chain`, `auto_rig_weight`,
`mirror_bones`, `reset_pose`, `pose_bone`, `add_armature_modifier` (tanpa weight paint,
background-safe). Bone collections (API 4.0+).

### Animación
`insert_keyframe`, `animate_location/rotation/scale`, `keyframe_animation`,
`create_action`, `set_keyframe_interpolation` (CONSTANT/LINEAR/BEZIER),
`set_render_range`, `set_frame`, `add_shape_key`, `list_shape_keys`,
`add_rigid_body`, `set_gravity`, `clear_keyframes`.

### Escena / luces / cámara / render
`create_light` (POINT/SUN/SPOT/AREA), `setup_three_point_lighting`,
`create_camera`, `set_camera_target`, `set_camera_active`,
`set_render_engine` (CYCLES/EEVEE/WORKBENCH), `set_render_resolution`,
`set_render_samples`, `set_cycles_device`, `render_frame`,
`scene_summary`, `cleanup_scene`, `purge_orphans`, `select_by_type`,
`hide_object`, `jump_to_view3d_object_by_name`.

### UV · Impresión 3D · Batch · Análisis · Geometry Nodes · IO
`unwrap_object` (SMART/PLANAR/CUBE/SPHERE/CYLINDER, background-safe),
`add_uv_map`, `texel_density` · `check_manifold`, `set_dimensions_mm`,
`add_wall_thickness`, `bed_layout`, `export_stl_mm` · `batch_rename`,
`batch_delete_by_type`, `apply_transforms_all`, `batch_duplicate` ·
`get_objects_summary`, `get_object_detail_summary`, `mesh_analysis`,
`get_blendfile_summary_datablocks`, `analyze_performance` ·
`scatter_instances` (GN), `add_geometry_nodes_modifier`, `gn_add_node` ·
`export_scene/export_selected/import_file` (glb/gltf/fbx/obj/stl/ply/usd/usdz/dae/x3d).

### Compatibilidad Blender 5.x
- `blender_version_min = "4.2.0"` (manifest + `bl_info`)
- `addon/compat.py`: gates de versión para `temp_override`, bone collections,
  muestras de EEVEE Next y device de Cycles
- La geometría se crea con data API / bmesh (funciona en `blender -b`); solo
  features que requieren UI (monkey, auto-weights, screenshots) devuelven un
  mensaje claro en modo background
- Verificación offline: `tests/bpy_stub.py` + `tests/test_command_surface.py`
  ejecutan las 71 órdenes documentadas sin binario de Blender
