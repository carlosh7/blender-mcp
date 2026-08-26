# blender-mcp-ultra — Changelog

## v3.0.0 (2026-08-25) — Edición Axiom v3.0

### Features
- **217 tools registry · 223 vía MCP** (gateway único `mcp_server.py`: 6 base + registro dinámico por socket)
- **Seguridad P0 cerrada**: mini_http solo localhost + token `X-API-Token`, sandbox en `execute_blender_code`, 0 leaks en historia (gitleaks), CI con bandit/pip-audit/gitleaks
- **Bus de eventos**: ring buffer + `poll_events` (render, locks, snapshots)
- **Multi-escena real**: `scene.list_scenes`, `copy_object_to`, render por escena
- **Física completa**: particles, soft_body, presets, constraints, bake_cache (compat Blender 5.x)
- **Export avanzado**: `export.game_collision`, `export.lods`, `export.batch`, `export.for_target` + `perf.*` (9 tools)
- **VLM feedback**: capture (viewport o EEVEE headless) + analyze/quick/composition/lighting
- **Collab**: locks por objeto, mensajería, tareas, workflows + `asset_library` + blueprints 27-pt (20 tools)
- **Planner/docs/version_control**: `plan.*`, `docs.*`, `vc.*` (10 tools)
- **Compositor**: node_add/set_input/connect/list_nodes (Blender 5.x)
- **Skills y recetas**: docs/skills con workflows probados E2E en Blender 5.1
- **Empaquetado extensión**: `blender_manifest.toml` + `scripts/build_extension.py`

### Removed (deprecados v2.2 → eliminados)
- `addon/stdio_bridge.py` → sustituido por el gateway `mcp_server.py` (auto_config actualizado)
- `addon/export_manager.py` → usar `src/tools/io` + `export.for_target`
- `addon/collaborative.py` → usar tools `collab.*` (backend `multi_agent.py`)
- Comandos socket `collab_register/lock/unlock/status` eliminados de `_axsock.py`

### Fixed
- Doble registro del addon, mapeo de `bound_box` en anclas 27-pt, `_introspect_ops` sin `max_results`
- Imports absolutos → paquete instalable; pins de `mcp[cli]>=1.3,<2`
- Handlers duplicados en `_axsock.py`; física compatible con Blender 5.x

### Quality
- **479 tests passed** · ruff limpio · bandit sin HIGH · pip-audit sin vulnerabilidades

## v2.0.0 (2026-08-04)

### Features
- **AI Integration**: Real AI with Ollama (phi3:mini)
- **Text→3D**: Create 3D objects from natural language
- **Voice Control**: Voice commands for creating objects
- **Scene Analysis**: Analyze scene with perception system
- **Quality Check**: Verify scene quality (100/100)
- **Reference Compare**: Compare scene with expectations
- **Building Generator**: Create buildings with windows
- **Character Gen**: Create humanoid characters
- **Physics Engine**: Cloth, Rigid Body, Soft Body, Particles
- **Animation System**: Keyframes, walk cycles
- **Material Library**: 50+ PBR materials
- **Export Engine**: FBX, OBJ, glTF, STL, USD, Alembic

### Improvements
- Error handling in all modules
- bpy import checks for offline testing
- Comprehensive test suite
- Complete documentation

### Bug Fixes
- Fixed duplicate class registration in UI
- Fixed bpy import errors
- Fixed syntax errors in sculpt_engine

## v1.0.0 (2026-08-03)

### Initial Release
- Socket Server TCP :9876
- Basic mesh engine
- Basic texture engine
- Basic rig engine
- Basic animation engine
- Character generator
- Physics engine
- Perception system
- AI assistant (placeholder)
- UI Panel (basic)
