# blender-mcp — Documentación Completa de Investigación y Desarrollo

> **Fecha:** 2026-05-14
> **Versión actual:** v0.8.53
> **Objetivo:** Documentar todas las decisiones de arquitectura, investigación de proyectos similares, lecciones aprendidas y plan futuro.

---

## Índice

1. [Proyectos Investigados](#1-proyectos-investigados)
2. [Arquitectura Actual](#2-arquitectura-actual)
3. [Decisiones de Diseño](#3-decisiones-de-diseño)
4. [Historial de Versiones y Bugs](#4-historial-de-versiones-y-bugs)
5. [Tools Implementadas](#5-tools-implementadas)
6. [Protocolo de Comunicación](#6-protocolo-de-comunicación)
7. [Lo que Falta vs Oficial](#7-lo-que-falta-vs-oficial)
8. [Referencias](#8-referencias)

---

## 1. Proyectos Investigados

### 1.1 ahujasid/blender-mcp (21.6k★)

| Atributo | Detalle |
|----------|---------|
| **URL** | https://github.com/ahujasid/blender-mcp |
| **Creador** | Siddharth Ahuja |
| **Licencia** | MIT |
| **Arquitectura** | Addon socket server + MCP server externo (FastMCP STDIO) |
| **Tools** | `execute_blender_code` como tool principal. No tiene tools de primitivas. |

**Características clave:**
- `addon.py` monolítico (socket server dentro de Blender, puerto 9876)
- `src/blender_mcp/server.py` (MCP server con FastMCP, STDIO)
- Usa `uv` para empaquetado (`uvx blender-mcp`)
- Poly Haven, Sketchfab, Hyper3D Rodin, Hunyuan3D como integraciones
- Captura de viewport para validación visual
- Telemetría anónima

**Lo que hace diferente:** Solo expone `execute_blender_code` como tool. Sin primitivas. El LLM genera código Python completo. No tiene loop de tool calling.

**Lección aprendida:** No se necesitan tools de primitivas. `execute_blender_code` es suficiente.

---

### 1.2 youichi-uda/blender-mcp-pro (15★, $15)

| Atributo | Detalle |
|----------|---------|
| **URL** | https://github.com/youichi-uda/blender-mcp-pro |
| **Precio** | $15 one-time / $5 mes |
| **Tools** | 120+ tools en 17 categorías |

**Categorías de tools:** Scene & Objects, Materials, Shader Nodes, Lights, Modifiers (22 tipos), Animation, Geometry Nodes, Camera, Render, Import/Export (12 formatos), UV & Texture (7 métodos), Batch Processing, Assets (Poly Haven, Sketchfab), Rigging, Rig Diagnostics, Scene Utilities, Workflows.

**Lección aprendida:** La organización por handlers modulares es el camino correcto.

---

### 1.3 yuri-schmaltz/mcp-blender (fork v2.6.0)

**Características adicionales:** Handlers modulares, 3D Printing Toolkit, Mesh Integrity, AmbientCG Integration, Product Studio, Vehicle Rigging, Extension mode, GUI PySide6, `--doctor`, tests E2E.

**Lección aprendida:** Los tests E2E y `--doctor` son críticos para diagnóstico.

---

### 1.4 AIGODLIKE/GenesisCore (119★)

**Características clave:** MCP Client + Server dentro de Blender (self-contained), 7 proveedores LLM, auto-instalación de pip, streaming output.

**Lección aprendida:** El modo self-contained es viable. La auto-instalación de dependencias es necesaria.

---

### 1.5 3DSceneAgent/Vibe3DScene (85★)

**Arquitectura:** LangGraph + FastAPI + Redis + Web UI (React+TypeScript). Orquestación multi-agente, headless Blender, multi-worker.

---

### 1.6 Blender.org MCP Server (Oficial, v1.0.0)

| Atributo | Detalle |
|----------|---------|
| **URL** | https://www.blender.org/lab/mcp-server/ |
| **Repo** | https://projects.blender.org/lab/blender_mcp |
| **Versión** | 1.0.0 |
| **Requisito** | Blender 5.1+ |

**Archivos del addon (9 archivos):** `__init__.py`, `mcp_to_blender_server.py`, `execute_blocking.py`, `execute_interactive.py`, `weak_sandbox.py`, `capture_output.py`, `deferred_tool.py`, `cli.py`, `blender_manifest.toml`.

**Tools del MCP server (~20):**
- `execute_blender_code` — Tool principal
- `get_objects_summary`, `get_object_detail_summary` — Análisis de escena
- `get_blendfile_summary_datablocks`, `get_blendfile_summary_usage_guess` — Data-blocks
- `get_screenshot_of_area_as_image`, `get_screenshot_of_window_as_image` — Captura visual
- `render_thumbnail_to_path`, `render_viewport_to_path` — Render
- `search_api_docs`, `search_manual_docs`, `get_python_api_docs` — Documentación
- `jump_to_view3d_object_by_name`, `jump_to_tab_by_name` — Navegación

**Incluye documentación de API embebida:** Archivos `.rst` de toda la API de Blender + motor de búsqueda.

**Protocolo:** Socket TCP :9876, mensajes delimitados por NULL byte (`\0`).

---

### 1.7 cc-blender-skill (2★)

30 skills Claude Code encadenables: text-to-blender, modeling, materials, lighting, cameras, rendering, animation, export, wireframe-to-3d, pro-workflow.

---

### 1.8 Claude Desktop Blender Connector

Conector oficial de Anthropic. Solo funciona con Claude Desktop (no browser). El flujo: Claude Desktop → Connector → Addon Blender → bpy.

---

## 2. Arquitectura Actual

```
CLIENTES EXTERNOS              SERVIDOR MCP                BLENDER
opencode ──STDIO──▶ mcp_server.py ──Socket──▶ addon/
Claude Desktop      (FastMCP)      :9876      ├─ _axsock.py
Cursor              (82 tools)                ├─ handlers/ (22)
                                              ├─ auto_process.py
                                              ├─ panels/
                                              └─ operators/
```

### Chat Interno (sin MCP externo)

```
Usuario → auto_process._tick() (cada 0.5s)
  → _call_llm() → API REST → texto con código
  → _exec_code() → ejecuta en Blender
  → _respond() → muestra en chat
```

---

## 3. Decisiones de Diseño

### 3.1 Tool Calling vs Texto Plano

| Decisión | Estado | Razón |
|----------|--------|-------|
| Tool calling con TOOLS_DEF | ❌ Eliminado v0.8.48 | Loop 6 turnos = 30-60s |
| Texto plano con código en bloques | ✅ Actual | 1 llamada = 3-10s |

### 3.2 Primitivas vs execute_blender_code

| Decisión | Estado | Razón |
|----------|--------|-------|
| Tools de primitivas | ❌ Eliminado v0.8.47 | Limitan al LLM |
| Solo execute_blender_code | ✅ Actual | Acceso completo a API |

### 3.3 TOOLS_DEF Simplificado (4 tools)

```python
TOOLS_DEF = [
    execute_blender_code,     # Crear cualquier cosa en Blender
    get_scene_info,           # Ver la escena
    get_viewport_screenshot,  # Validación visual
    scene_summary,            # Resumen de escena
]
```

### 3.4 Tabla de Versiones Clave

| Versión | Cambio |
|---------|--------|
| v0.8.20 | Renombrar blender_socket → _axsock |
| v0.8.26 | Eliminar SSE server (uvicorn freeze) |
| v0.8.42 | 64/64 tools validadas |
| v0.8.48 | Eliminar tool calling → texto directo |
| v0.8.53 | Blender 4.2 LTS target |

---

## 4. Bugs Resueltos

| Bug | Causa | Solución | Versión |
|-----|-------|----------|---------|
| Blender congelado | uvicorn.run en thread | Eliminar SSE server | v0.8.26 |
| Chat no actualiza | tag_redraw no forzaba todas las áreas | for area in screen.areas | v0.8.29 |
| Socket: Offline | Panel dependía de timer | Verificar directo | v0.8.16+ |
| Unknown command | __import__ package name incorrecto | Detectar __package__ | v0.8.39 |
| _socket_server None | Dos módulos _axsock | Unificar imports relativos | v0.8.36 |
| reasoning_content error | DeepSeek modo thinking | Usar raw_message | v0.8.36 |
| BaseHandler blocking | Dispatch encontraba BaseHandler primero | Saltar BaseHandler | v0.8.40 |
| StructRNA removed | self.model_id expiraba en thread | Variable local | v0.8.27 |
| Context.active_object None | bpy.context.active_object en thread | Detectar por nombre | v0.8.46 |
| ZIP addon duplicado | Carpeta addon/ genérica | Carpeta axiom_engine/ | v0.8.2 |
| externally-managed | PEP 668 | --break-system-packages | v0.8.10 |

---

## 5. Tools Implementadas (22 handlers)

| Handler | Comandos |
|---------|----------|
| Scene | get_scene_info, get_object_info, ping, execute_code |
| Objects | create, delete, transform, duplicate, select |
| Materials | create, assign, set_color, list |
| Modifiers | add, remove, list, apply (22 tipos) |
| Lights | create, three_point_lighting |
| Camera | create, set_target, auto_frame |
| Animation | keyframe, animate_location/rotation/scale, action, interpolation, render_range |
| Shader Nodes | add, connect, set_value, list, remove (40+ tipos) |
| Geometry Nodes | add_modifier, add_node, connect, scatter, list |
| Render | engine, resolution, samples, frame, cycles_device |
| IO | export, import (12 formatos) |
| UV & Texture | unwrap (7 métodos), add_map, bake, list |
| Batch | turntable, rename, delete, apply_transforms |
| Rigging | armature, bone, vertex_group, constraint, parent, auto_weight |
| Scene Utils | purge, cleanup, mesh_analysis, summary, select_by_type, hide, join |
| 3D Printing | manifold, mm_dimensions, stl_export, bed_layout, wall_thickness |
| Poly Haven | search, categories, status, download HDRI/texture/model |
| Sketchfab | search, status, preview, download |
| Hyper3D Rodin | status, create_job, poll, import |
| Hunyuan3D | status, create_job, poll, import |
| AmbientCG | search, categories, download |
| (Analysis) | Planificado |

---

## 6. Lo que el Oficial tiene que Nosotros NO

| Tool oficial | Prioridad | Esfuerzo |
|-------------|-----------|----------|
| `get_objects_summary` | 🔴 Alta | 2h |
| `get_object_detail_summary` | 🔴 Alta | 2h |
| `get_blendfile_summary_datablocks` | 🟡 Media | 1h |
| `get_screenshot_of_area_as_image` | 🟡 Media | 2h |
| `render_viewport_to_path` | 🟡 Media | 1h |
| `search_api_docs` | 🟢 Baja | 4h |
| `jump_to_view3d_object_by_name` | 🟢 Baja | 1h |

---

## 7. Referencias

| Recurso | URL |
|---------|-----|
| ahujasid/blender-mcp | https://github.com/ahujasid/blender-mcp |
| youichi-uda/blender-mcp-pro | https://github.com/youichi-uda/blender-mcp-pro |
| Blender.org MCP | https://www.blender.org/lab/mcp-server/ |
| Claude Blender Tutorial | https://claude.com/resources/tutorials/using-the-blender-connector-in-claude |
| Nuestro repo | https://github.com/carlosh7/blender-mcp |
| Nuestro ZIP | https://github.com/carlosh7/blender-mcp/blob/main/dist/axiom_engine_v0.8.53.zip |
| Discord comunidad | https://discord.gg/z5apgR8TFU |
