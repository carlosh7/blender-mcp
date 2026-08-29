# blender-mcp-ultra — Changelog

## v3.2.0 (2026-08-28) — "Lite, Seguro y Guiado"

### Added
- **Guías de workflow dentro del MCP** (`guidance.list` / `guidance.get`):
  22 guías de técnica y pipeline (animación, iluminación, render, escena de
  producto...) empaquetadas en el wheel y servidas bajo demanda — el agente
  las pide cuando el workflow se complica, con coste de contexto ~0 hasta
  entonces. Sustituye a las skills instalables: cero fricción para el usuario
- **Modo lite del gateway** (`--lite`, `--lite` en `blender-mcp`, o
  `BLENDER_MCP_LITE=1`): registra 24 tools (7 base + 17 núcleo) en vez de
  245 — reduce el coste de contexto por petición de ~30k a ~4k tokens sin
  perder capacidad: `tools_search` descubre el resto del registry y
  `tool_execute` lo ejecuta (acepta `material.pbr` o `material_pbr`)
- **Estrategia de docs RST**: `scripts/fetch_docs_data.py` descarga
  `data/` del release; los tests de `rst_search` se omiten si no hay datos

### Changed
- **Paquete `src/` renombrado a `mcp_ultra/`**: el wheel ya no instala un
  paquete top-level llamado `src` en site-packages (colisiones casi
  garantizadas); entry point `blender-mcp-server` actualizado
- CLI: `--mode sse` ahora funciona (respetaba envs que el gateway ignoraba);
  `start/stop` encontraban el server script en una ruta equivocada;
  `ARCHITECTURE.md` reescrito a la arquitectura actual

### Security
- **mini_http (REST :9877)**: todo acceso a bpy se serializa al hilo principal
  vía `bpy.app.timers` (antes `exec()` desde el hilo HTTP — bpy no es
  thread-safe); token unificado con el del socket vía archivo compartido
  (**ya no se guarda en la escena .blend**, viajaba con el archivo); body
  limitado a 1 MB
- **Sin `SO_REUSEPORT`** en el socket :9876: en Linux permitía a otro proceso
  bindear el mismo puerto y robar parte del tráfico
- README: claims de seguridad ajustadas a la realidad (~80 patrones AST en
  gateway+addon, sin "sandbox de subprocess" no cableado)
- **Auth obligatoria en el socket :9876**: si no hay `BLENDER_MCP_TOKEN` ni
  token de escena, el addon genera uno (`secrets.token_hex`) y lo persiste en
  `<config>/blender-mcp/socket_token` (0600); el gateway lo lee del mismo
  archivo — cero configuración, ningún comando anónimo en localhost
- **`code_guard` (AST blocklist) cableado en `cmd_execute_code`** del addon:
  la vía principal ya no ejecuta código sin validar (antes solo protegía la
  ruta HTTP :9877)
- **Eliminado `_strip_bad_code`**: el addon ya no reescribe silenciosamente
  el código del agente (borraba `unlink(...)` y quitaba los `/2` de
  `.scale = (...)`, corrompiendo la intención)

### Fixed
- **El gateway registra el registry completo sin Blender**: `mcp_server.py`
  leía los metadatos de las 239 tools por socket una sola vez al arrancar;
  si el addon no estaba arriba, el cliente MCP quedaba con 6 tools para
  siempre. Ahora construye el mismo `ToolRegistry` en local
  (fallback socket) — el orden de arranque cliente/Blender ya no importa y
  las tools funcionan en cuanto Blender se abre. Verificado E2E: venv limpio
  + wheel → `blender-mcp-server` → 245 tools → ejecución real
- **`execute_code` en Windows**: `signal.SIGALRM` no existe ahí y rompía cada
  llamada; ahora el timeout se aplica solo donde está disponible
- **Concurrencia en `blender_connection`**: lock por petición — llamadas MCP
  simultáneas ya no pueden intercalar `sendall`/`recv` y cruzar respuestas
- Fuga de socket en `cmd_diagnose`; tests e2e actualizados al gateway
  canónico (sesión MCP reutilizable + token)
- **Contenido no-Python del wheel**: el patrón `data/` del `.gitignore`
  hacía que hatchling excluyera los directorios `data/` empaquetados —
  `tools_index.json` (tools_search) no viajaba en el wheel y quedaba roto
  en installs de pip. Renombrados a `guidance/guides/` y
  `context_search/index/`

### Removed
- **`skills/` consolidado**: los 29 SKILL.md (7 pares duplicados con dos
  esquemas de nombre, sin frontmatter) se deduplicaron a 22 guías canónicas
  que ahora viajan dentro del MCP vía `guidance.*` — las skills instalables
  a mano ya no existen como mecanismo
- **`data/` (27 MB, 4.400 archivos RST) fuera de git**: se descargan con
  `python scripts/fetch_docs_data.py` desde el release asset
  [`docs`](https://github.com/carlosh7/blender-mcp/releases/tag/docs);
  tests de `rst_search` se omiten sin datos
- **Gateways legacy**: `mcp_adapter.py` (auth auto-bypass, protocolo viejo) y
  `start_server.py` (exec sin guard); `src/tools/registry.py` (segundo
  ToolRegistry sin uso) y su test. Solo queda el gateway canónico
  `mcp_server.py` (entry points `blender-mcp` y `blender-mcp-server`)
- **Pila legacy "AXIOM" del addon** (~5.500 líneas, 0 importers): raíz
  `__init__.py`, `properties/preferences/chat_types`, `operators/`,
  `panels/`, `client/`, `auto_process`, `ai_assistant_clean`,
  `weak_sandbox`, `execution_queue`, `asset_cache`, `deferred_tool`,
  `progress_reporter`, `error_handler`, `perception_helper`
- 10 scripts legacy de raíz (tests/stress duplicados por `tests/`); los 9
  generadores de escena movidos a `examples/`

### Changed
- docs/clients/ (Claude Code/Desktop, Cursor, opencode, VS Code, Windsurf):
  receta canónica `pip install blender-mcp-ultra` + `blender-mcp-server`;
  README con conteos sincronizados (245 tools)
- pyproject: URLs del repo corregidas (apuntaban a un repo inexistente)
- CI: `ruff format` de `scripts/gen_tools_index.py` (job de lint en rojo)

## v3.1.0 (2026-08-26) — "Spatial & Eyes + Agent Experience"

### Added (22 tools nuevas → 239 total)
- **Agent Experience** (de ciclos reales agente↔Blender): `scene.mark/diff`,
  `object.place_bottom` (colocación bbox-aware), `object.snap_to`,
  `render.preview`, `camera.check` (frustum), `physics.bake/free_cache`,
  `scene.cleanup` (duplicados/empties/escala/huérfanos)
- **Inteligencia espacial**: `spatial.place/query/check_move/dimensions/floorplan/stack`
  + DB de dimensiones reales (60 objetos)
- **Eyes sin VLM**: `inspect.view` (silhouette/wireframe/uv_checker/normals),
  `inspect.turntable`, `inspect.topology` (score 0-100)
- **Economía de contexto**: `tools.search` (índice generado en build)
- **scene.explain** — objeto/materiales/nodos explicados en NL
- **Presets & Moods**: `scene.preset` (10 entornos), `scene.mood` (6 iluminaciones)
- `docs/skills/scene-building-guide.md` — guía de construcción para agentes

### Fixed
- **Crítico**: la extensión instalada limpia no exponía el registry (0 tools):
  ahora empaqueta src/ + blender_mcp/ y el loader prueba múltiples raíces
- Servidor headless: ceder turno entre clientes (0.5s idle) — concurrencia 10/10
- Helpers de tests: recepción en loop (respuestas >64KB llegan fragmentadas)

## v3.0.2 (2026-08-26)

### Fixed
- **El wheel ahora incluye el gateway canónico** (`mcp_server.py`,
  `mcp_adapter.py`, `blender_connection.py`, `config.py`): el entry point
  `blender-mcp-server` funciona sin el repo (223 tools vía socket, verificado)

## v3.0.1 (2026-08-26)

### Fixed
- Publicación en PyPI con todos los fixes incluidos (3.0.0 se subió antes de
  los últimos commits): anotaciones `bpy` lazy en py<3.14, rutas cross-OS
  del addon, fixes de CI

### Added
- docs/clients/claude-code.md, galería de renders showcase en el README
- SEO: topics, descripción y social preview del repo

## Unreleased (post-v3.0.0)

### Added
- **Cross-OS real**: rutas temporales portables en 11 módulos del addon
  (`addon/_paths.py`); adiós a los `/tmp` hardcodeados que rompían Windows
- **CI multi-OS**: job `test-os` con windows-latest y macos-latest (unit tests)
- **docs/clients/claude-code.md**: registro en un comando (`claude mcp add`)
- **Dockerfile**: gateway MCP remoto por SSE (verificado E2E)

### Fixed
- `mcp_server --sse`: host/puerto configurables (`MCP_SSE_HOST`/`MCP_SSE_PORT`)
- CI: anotaciones `bpy.types` sin Blender en py<3.14, race SIGXCPU en
  `sandbox_real`, tests dependientes de máquina local

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
