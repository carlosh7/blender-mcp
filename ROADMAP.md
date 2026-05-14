# blender-mcp Roadmap

> **Visión**: El sistema MCP para Blender más completo, flexible y compatible con cualquier cliente MCP (Claude, opencode, Cursor, VS Code, Antigravity, LM Studio, Ollama, etc.)

---

## Principios de Arquitectura

1. **Dual-mode agent**: Modo "proxy" (rápido, delega loop a Claude/Cursor externo) + modo "autónomo" (embebido, multi-provider, sin dependencias externas)
2. **Modular tool system**: Tools organizadas por categoría, carga perezosa (lazy loading)
3. **Multi-cliente**: STDIO para clientes MCP estándar, SSE para persistencia, HTTP REST para Antigravity/custom
4. **Blender 4.2+**: Target principal con soporte para Extensiones, retrocompatibilidad 4.0+
5. **Open standard**: 100% MCP Protocol, sin vendor lock-in

---

## Fase 0: Fundación (Semana 1) — P0 🔴

### Objetivo: Empaquetado, distribución y arquitectura base

| # | Tarea | Archivos | Depende de |
|---|-------|----------|------------|
| 0.1 | Crear `pyproject.toml` para distribución uv/pip | `pyproject.toml`, `uv.lock` | — |
| 0.2 | Entry point unificado `blender-mcp` CLI | `src/blender_mcp/cli.py` | 0.1 |
| 0.3 | Reestructurar a paquete Python instalable | `src/blender_mcp/__init__.py`, `src/blender_mcp/server.py`, `src/blender_mcp/config.py` | 0.1 |
| 0.4 | Sistema de logging configurable (env vars) | `src/blender_mcp/logger.py` | 0.2 |
| 0.5 | Health check `--doctor` | `src/blender_mcp/doctor.py` | 0.2 |
| 0.6 | Unificar `server.py` + `mcp_server.py` en un solo server | `src/blender_mcp/server.py` (refactor) | 0.3 |

**Estimación**: 3-4 días

---

## Fase 1: Panel Híbrido (Semana 1-2) — P0 🔴

### Objetivo: Unificar el panel actual (chat + modelo selector) con los toggles de integraciones de ahujasid

| # | Tarea | Archivos | Depende de |
|---|-------|----------|------------|
| 1.1 | Checkbox "Use Poly Haven" + estado | `addon/panels/main.py`, `addon/properties.py` | 0.6 |
| 1.2 | Checkbox "Use Sketchfab" + API Key input | `addon/panels/main.py`, `addon/properties.py` | 1.1 |
| 1.3 | Checkbox "Use Hyper3D Rodin" + modo + API Key + botón Free Trial | `addon/panels/main.py`, `addon/properties.py` | 1.2 |
| 1.4 | Checkbox "Use Hunyuan3D" + modo + parámetros | `addon/panels/main.py`, `addon/properties.py` | 1.3 |
| 1.5 | Telemetry consent en Preferences | `addon/preferences.py` | 1.4 |
| 1.6 | Botones "Local Setup" (Install deps, Copy config, Open logs, Health check) | `addon/panels/main.py`, `addon/operators/setup.py` | 1.5 |
| 1.7 | Refactor panel actual a tabs: Chat + Integrations + Config | `addon/panels/chat.py`, `addon/panels/integrations.py`, `addon/panels/config.py` | 0.6 |

**Estimación**: 4-5 días

---

## Fase 2: Integraciones de Assets Reales (Semana 2-3) — P0 🔴

### Objetivo: Reemplazar todos los mocks con implementaciones reales

| # | Tarea | Archivos | Depende de |
|---|-------|----------|------------|
| 2.1 | Poly Haven real: search + download HDRI/textures/models + cache | `addon/handlers/polyhaven.py`, `src/blender_mcp/tools/polyhaven.py` | 0.6, 1.1 |
| 2.2 | Sketchfab real: search + preview thumbnail + download glTF | `addon/handlers/sketchfab.py`, `src/blender_mcp/tools/sketchfab.py` | 0.6, 1.2 |
| 2.3 | Hyper3D Rodin real: job submission + polling + import pipeline | `addon/handlers/hyper3d.py`, `src/blender_mcp/tools/hyper3d.py` | 0.6, 1.3 |
| 2.4 | Hunyuan3D real: text/image → model 3D | `addon/handlers/hunyuan.py`, `src/blender_mcp/tools/hunyuan.py` | 0.6, 1.4 |
| 2.5 | Asset cache system (evitar redescargar) | `src/blender_mcp/cache.py` | 2.1 |
| 2.6 | AmbientCG integration (de yuri-schmaltz) | `addon/handlers/ambientcg.py` | 2.5 |

**Estimación**: 5-7 días

---

## Fase 3: 120+ Tools MCP (Semana 3-5) — P1 🟡

### Objetivo: Implementar herramientas modulares por categoría (inspirado en youichi-uda/blender-mcp-pro)

| # | Categoría | Archivos | Tools estimadas |
|---|-----------|----------|-----------------|
| 3.1 | Scene & Objects | `addon/handlers/objects.py`, `src/blender_mcp/tools/objects.py` | 10 |
| 3.2 | Materials (Principled BSDF) | `addon/handlers/materials.py`, `src/blender_mcp/tools/materials.py` | 8 |
| 3.3 | Shader Nodes (full tree control) | `addon/handlers/shader_nodes.py`, `src/blender_mcp/tools/shader_nodes.py` | 10 |
| 3.4 | Lights (Point/Sun/Spot/Area + 3-point) | `addon/handlers/lights.py`, `src/blender_mcp/tools/lights.py` | 6 |
| 3.5 | Modifiers (22 tipos) | `addon/handlers/modifiers.py`, `src/blender_mcp/tools/modifiers.py` | 22 |
| 3.6 | Animation (keyframes, F-curves, NLA) | `addon/handlers/animation.py`, `src/blender_mcp/tools/animation.py` | 8 |
| 3.7 | Geometry Nodes (build networks, scatter) | `addon/handlers/geometry_nodes.py`, `src/blender_mcp/tools/geometry_nodes.py` | 8 |
| 3.8 | Camera (lens, DOF, tracking, auto-framing) | `addon/handlers/camera.py`, `src/blender_mcp/tools/camera.py` | 6 |
| 3.9 | Render (engine, cycles/eevee, output) | `addon/handlers/render.py`, `src/blender_mcp/tools/render.py` | 6 |
| 3.10 | Import/Export (FBX, OBJ, GLTF, USD, STL...) | `addon/handlers/io.py`, `src/blender_mcp/tools/io.py` | 9 |
| 3.11 | UV & Texture (7 unwrap methods, baking) | `addon/handlers/uv_texture.py`, `src/blender_mcp/tools/uv_texture.py` | 8 |
| 3.12 | Batch Processing (multi-camera, turntable) | `addon/handlers/batch.py`, `src/blender_mcp/tools/batch.py` | 4 |
| 3.13 | Rigging (armature, bones, constraints) | `addon/handlers/rigging.py`, `src/blender_mcp/tools/rigging.py` | 8 |
| 3.14 | Scene Utilities (cleanup, rename, mesh analysis) | `addon/handlers/scene_utils.py`, `src/blender_mcp/tools/scene_utils.py` | 6 |
| 3.15 | 3D Printing (mm-scale, manifold, bed layout) | `addon/handlers/printing.py`, `src/blender_mcp/tools/printing.py` | 6 |

**Total estimado**: ~125 tools

**Estimación**: 10-14 días

---

## Fase 4: Velocidad del Agente (Semana 3-4, paralela a Fase 3) — P1 🟡

### Objetivo: Optimizar el agente autónomo + añadir modo proxy

| # | Tarea | Archivos | Depende de |
|---|-------|----------|------------|
| 4.1 | Modo proxy: detectar cliente MCP externo y delegar loop | `src/blender_mcp/proxy.py`, `agent_host.py` (refactor) | 0.6 |
| 4.2 | Reducir MAX_TURNS de 10 a 5 | `agent_host.py` | — |
| 4.3 | Streaming de respuestas LLM | `agent_host.py`, `src/blender_mcp/streaming.py` | 0.6 |
| 4.4 | Cache de herramientas (get_scene_info, etc.) | `src/blender_mcp/tool_cache.py` | 4.3 |
| 4.5 | Timer queue a lo GenesisCore (no bloquear UI de Blender) | `addon/timer_queue.py` | 0.6 |
| 4.6 | Parallel tool calls cuando no hay dependencias | `agent_host.py` | 4.5 |
| 4.7 | Historial de memória optimizado (solo contexto relevante) | `agent_host.py` | 4.3 |

**Estimación**: 4-6 días (puede hacerse en paralelo con Fase 3)

---

## Fase 5: Recursos MCP y Schema Enriquecido (Semana 5) — P1 🟡

### Objetivo: Exponer estado de Blender como recursos MCP + schemas más ricos

| # | Tarea | Archivos | Depende de |
|---|-------|----------|------------|
| 5.1 | Resource `blender://scene/info` | `src/blender_mcp/resources.py` | 0.6 |
| 5.2 | Resource `blender://scene/objects` | `src/blender_mcp/resources.py` | 5.1 |
| 5.3 | Resource `blender://scene/materials` | `src/blender_mcp/resources.py` | 5.1 |
| 5.4 | Prompt `asset_creation_strategy()` (como ahujasid) | `src/blender_mcp/prompts.py` | 0.6 |
| 5.5 | Prompt `scene_analysis_strategy()` (como blender.org) | `src/blender_mcp/prompts.py` | 5.4 |
| 5.6 | Prompt `geometry_nodes_document()` (del oficial) | `src/blender_mcp/prompts.py` | 5.5 |
| 5.7 | Image responses (screenshots como Image MCP) | `src/blender_mcp/server.py` | 0.6 |
| 5.8 | Tool schemas con descripciones detalladas para mejor comprensión del LLM | `src/blender_mcp/tools/*.py` | 3.x |

**Estimación**: 3-4 días

---

## Fase 6: Multi-Cliente y Compatibilidad (Semana 5-6) — P2 🟢

### Objetivo: Documentar y configurar para todos los clientes MCP del mercado

| # | Tarea | Archivos | Depende de |
|---|-------|----------|------------|
| 6.1 | Claude Desktop connector oficial | `docs/claude-desktop.md` | 0.1 |
| 6.2 | Cursor integration + `.cursor/mcp.json` | `docs/cursor.md` | 0.1 |
| 6.3 | VS Code integration | `docs/vscode.md` | 0.1 |
| 6.4 | Windsurf integration | `docs/windsurf.md` | 0.1 |
| 6.5 | LM Studio + Continue + Ollama | `docs/local-llm.md` | 0.1 |
| 6.6 | opencode integration (actualizar docs) | `docs/opencode.md` | 0.1 |
| 6.7 | Antigravity via HTTP Bridge (docs) | `docs/antigravity.md` | 0.6 |
| 6.8 | Docker/remote host support | `docs/remote.md`, `Dockerfile` | 0.6 |

**Estimación**: 2-3 días

---

## Fase 7: Calidad y Telemetría (Semana 6-7) — P2 🟢

### Objetivo: Tests, telemetría, logging, estabilidad

| # | Tarea | Archivos | Depende de |
|---|-------|----------|------------|
| 7.1 | Telemetría anónima configurable | `src/blender_mcp/telemetry.py`, `addon/preferences.py` | 1.5 |
| 7.2 | Decorador `@telemetry_tool` | `src/blender_mcp/telemetry_decorator.py` | 7.1 |
| 7.3 | Tests E2E conexión socket | `tests/test_e2e_socket.py` | 0.6 |
| 7.4 | Tests unitarios MCP server | `tests/test_server.py` | 0.6 |
| 7.5 | Tests de cada handler | `tests/test_handlers/` | 3.x |
| 7.6 | CI/CD con GitHub Actions | `.github/workflows/test.yml` | 7.3 |
| 7.7 | Logging configurable (nivel, formato, archivo) | `src/blender_mcp/logger.py` (completar) | 0.4 |

**Estimación**: 3-4 días

---

## Fase 8: Skills para Claude Code (Semana 7-8) — P3 🔵

### Objetivo: Crear skills markdown encadenables como cc-blender-skill

| # | Tarea | Archivos | Depende de |
|---|-------|----------|------------|
| 8.1 | Skill: text-to-blender (orquestador) | `skills/text-to-blender/SKILL.md` | 3.x |
| 8.2 | Skill: blender-modeling | `skills/blender-modeling/SKILL.md` | 8.1 |
| 8.3 | Skill: blender-materials | `skills/blender-materials/SKILL.md` | 8.1 |
| 8.4 | Skill: blender-lighting | `skills/blender-lighting/SKILL.md` | 8.1 |
| 8.5 | Skill: blender-cameras | `skills/blender-cameras/SKILL.md` | 8.1 |
| 8.6 | Skill: blender-rendering | `skills/blender-rendering/SKILL.md` | 8.1 |
| 8.7 | Skill: blender-animation | `skills/blender-animation/SKILL.md` | 8.1 |
| 8.8 | Skill: blender-export | `skills/blender-export/SKILL.md` | 8.1 |
| 8.9 | Skill: wireframe-to-3d | `skills/wireframe-to-3d/SKILL.md` | 8.2 |
| 8.10 | Skill: blender-pro-workflow | `skills/blender-pro-workflow/SKILL.md` | 8.1 |

**Estimación**: 5-7 días

---

## Fase 9: Modo Self-Contained (Semana 8-9) — P3 🔵

### Objetivo: MCP client + server dentro de Blender (tipo GenesisCore) para 0 dependencias externas

| # | Tarea | Archivos | Depende de |
|---|-------|----------|------------|
| 9.1 | MCP client base dentro de Blender | `addon/client/__init__.py`, `addon/client/base.py` | 0.6 |
| 9.2 | Provider: OpenAI-compatible | `addon/client/openai.py` | 9.1 |
| 9.3 | Provider: DeepSeek | `addon/client/deepseek.py` | 9.2 |
| 9.4 | Provider: Anthropic Claude | `addon/client/claude.py` | 9.2 |
| 9.5 | Provider: Ollama (local) | `addon/client/ollama.py` | 9.2 |
| 9.6 | SSE server embebido en Blender (local) | `addon/server/__init__.py`, `addon/server/server.py` | 9.1 |
| 9.7 | Auto-instalación de dependencias pip al activar | `addon/__init__.py` | 9.1 |
| 9.8 | Streaming output en editor de texto de Blender | `addon/ui/streaming.py` | 9.2 |
| 9.9 | Image input desde Blender al prompt | `addon/ui/image_input.py` | 9.2 |
| 9.10 | Config persistence por provider | `addon/config_cache.py` | 9.2 |

**Estimación**: 7-10 días

---

## Resumen de Timeline

```
Semana 1  │ Fase 0 ████████░░ Fase 1 ████░░░░░░░░░░░░░░░░
Semana 2  │ Fase 1 ██████████ Fase 2 ████░░░░░░░░░░░░░░░░
Semana 3  │ Fase 2 ██████████████ Fase 3 ████░░ Fase 4 ████░░
Semana 4  │ Fase 2 ██░░ Fase 3 ██████████ Fase 4 ██████░░░░
Semana 5  │ Fase 3 ██████░░ Fase 5 ████████ Fase 6 ██░░░░
Semana 6  │ Fase 5 ██░░ Fase 6 ██████░░ Fase 7 ████████░░
Semana 7  │ Fase 7 ██████░░ Fase 8 ████░░░░░░░░░░░░
Semana 8  │ Fase 8 ██████████ Fase 9 ████░░░░░░░░░░
Semana 9  │ Fase 9 ████████████
          │
P0 🔴     │ ████████████████████████████████████████ (Semanas 1-3)
P1 🟡     │ ██████████████████████████████░░░░░░░░ (Semanas 3-5)
P2 🟢     │ ████████████████████░░░░░░░░░░░░░░░░░░ (Semanas 5-7)
P3 🔵     │ ██████████████████████████████████████ (Semanas 7-9)
```

---

## Estructura Final de Archivos (Objetivo)

```
blender-mcp/
├── pyproject.toml              ← Empaquetado uv/pip
├── ARCHITECTURE.md             ← Documento de arquitectura
├── ROADMAP.md                  ← Este archivo
├── README.md
├── LICENSE
│
├── src/blender_mcp/            ← Paquete Python instalable
│   ├── __init__.py
│   ├── cli.py                  ← Entry point `blender-mcp`
│   ├── server.py               ← MCP Server principal (FastMCP)
│   ├── config.py               ← Configuración
│   ├── logger.py               ← Logging configurable
│   ├── doctor.py               ← Health check --doctor
│   ├── cache.py                ← Sistema de cache
│   ├── tool_cache.py           ← Cache de respuestas de tools
│   ├── proxy.py                ← Modo proxy para agentes externos
│   ├── streaming.py            ← Streaming de respuestas LLM
│   ├── telemetry.py            ← Telemetría anónima
│   ├── telemetry_decorator.py  ← Decorador @telemetry_tool
│   ├── resources.py            ← Recursos MCP (blender://)
│   ├── prompts.py              ← Prompts de estrategia
│   ├── tools/                  ← Tools MCP por categoría
│   │   ├── __init__.py
│   │   ├── scene.py
│   │   ├── objects.py
│   │   ├── materials.py
│   │   ├── shader_nodes.py
│   │   ├── lights.py
│   │   ├── modifiers.py
│   │   ├── animation.py
│   │   ├── geometry_nodes.py
│   │   ├── camera.py
│   │   ├── render.py
│   │   ├── io.py
│   │   ├── uv_texture.py
│   │   ├── batch.py
│   │   ├── rigging.py
│   │   ├── scene_utils.py
│   │   ├── printing.py
│   │   ├── polyhaven.py
│   │   ├── sketchfab.py
│   │   ├── hyper3d.py
│   │   └── hunyuan.py
│   └── agent/                  ← Agente autónomo
│       ├── __init__.py
│       ├── host.py             ← agent_host.py refactorizado
│       ├── memory.py           ← Persistencia de memoria
│       └── providers.py        ← Proveedores LLM
│
├── addon/                      ← Addon de Blender
│   ├── __init__.py             ← Registro principal
│   ├── bl_info.py              ← Metadatos del addon
│   ├── preferences.py          ← Telemetry consent + config
│   ├── properties.py           ← Propiedades de escena
│   ├── timer_queue.py          ← Timer queue (no bloquear UI)
│   ├── config_cache.py         ← Cache de config por provider
│   ├── panels/                 ← Paneles UI
│   │   ├── __init__.py
│   │   ├── main.py             ← Panel principal con toggles
│   │   ├── chat.py             ← Panel de chat
│   │   ├── integrations.py     ← Toggles de integraciones
│   │   └── config.py           ← Panel de configuración
│   ├── operators/              ← Operadores de Blender
│   │   ├── __init__.py
│   │   ├── connect.py          ← Connect/Disconnect
│   │   ├── chat.py             ← Send, Clear, Stop
│   │   ├── capture.py          ← Axiom Vision
│   │   ├── export.py           ← Axiom Export
│   │   └── setup.py            ← Local Setup buttons
│   ├── handlers/               ← Handlers de comandos socket
│   │   ├── __init__.py
│   │   ├── base.py             ← Handler base class
│   │   ├── scene.py
│   │   ├── objects.py
│   │   ├── materials.py
│   │   ├── shader_nodes.py
│   │   ├── lights.py
│   │   ├── modifiers.py
│   │   ├── animation.py
│   │   ├── geometry_nodes.py
│   │   ├── camera.py
│   │   ├── render.py
│   │   ├── io.py
│   │   ├── uv_texture.py
│   │   ├── batch.py
│   │   ├── rigging.py
│   │   ├── scene_utils.py
│   │   ├── printing.py
│   │   ├── polyhaven.py
│   │   ├── sketchfab.py
│   │   ├── hyper3d.py
│   │   ├── hunyuan.py
│   │   └── ambientcg.py
│   ├── client/                 ← MCP client embebido (Fase 9)
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── openai.py
│   │   ├── deepseek.py
│   │   ├── claude.py
│   │   └── ollama.py
│   ├── server/                 ← MCP server embebido (Fase 9)
│   │   ├── __init__.py
│   │   └── server.py
│   ├── ui/                     ← UI streaming (Fase 9)
│   │   ├── streaming.py
│   │   └── image_input.py
│   ├── blender_socket.py       ← Socket server (existente)
│   ├── assembly.py             ← Assembly engine (existente)
│   ├── scanner.py              ← Geometry scanner (existente)
│   ├── spatial.py              ← Spatial validator (existente)
│   └── assets.py               ← Asset manager (simplificado)
│
├── http_bridge.py              ← REST API (Antigravity)
├── agent_host.py               ← ← DEPRECATED, migrar a src/blender_mcp/agent/
│
├── skills/                     ← Skills para Claude Code (Fase 8)
│   ├── text-to-blender/SKILL.md
│   ├── blender-modeling/SKILL.md
│   ├── blender-materials/SKILL.md
│   ├── blender-lighting/SKILL.md
│   ├── blender-cameras/SKILL.md
│   ├── blender-rendering/SKILL.md
│   ├── blender-animation/SKILL.md
│   ├── blender-export/SKILL.md
│   ├── wireframe-to-3d/SKILL.md
│   └── blender-pro-workflow/SKILL.md
│
├── tests/                      ← Tests
│   ├── test_e2e_socket.py
│   ├── test_server.py
│   ├── test_config.py
│   └── test_handlers/
│
├── docs/                       ← Documentación
│   ├── claude-desktop.md
│   ├── cursor.md
│   ├── vscode.md
│   ├── windsurf.md
│   ├── local-llm.md
│   ├── opencode.md
│   ├── antigravity.md
│   └── remote.md
│
├── .github/workflows/          ← CI/CD
│   └── test.yml
│
├── Dockerfile                  ← Soporte remoto
└── generators/                 ← (existente, mantener)
```

---

## Dependencias entre Fases (Gráfico)

```
Fase 0 (Fundación)
   │
   ├──▶ Fase 1 (Panel Híbrido) ──▶ Fase 2 (Integraciones)
   │                                      │
   │                                      └──▶ Fase 3 (120+ Tools)
   │                                             │
   │                                             ├──▶ Fase 5 (Recursos MCP)
   │                                             ├──▶ Fase 8 (Skills)
   │                                             │
   └──▶ Fase 4 (Velocidad Agente) ──────────────┤
                                                 │
Fase 6 (Multi-Cliente) ◀─────────────────────────┤
                                                 │
Fase 7 (Calidad) ◀───────────────────────────────┘
                                                 │
Fase 9 (Self-Contained) ◀────────────────────────┘
```

---

## Estimación Total

| Fase | Días | Prioridad |
|------|------|-----------|
| Fase 0: Fundación | 3-4 | 🔴 P0 |
| Fase 1: Panel Híbrido | 4-5 | 🔴 P0 |
| Fase 2: Integraciones Reales | 5-7 | 🔴 P0 |
| Fase 3: 120+ Tools | 10-14 | 🟡 P1 |
| Fase 4: Velocidad Agente | 4-6 | 🟡 P1 |
| Fase 5: Recursos MCP | 3-4 | 🟡 P1 |
| Fase 6: Multi-Cliente | 2-3 | 🟢 P2 |
| Fase 7: Calidad | 3-4 | 🟢 P2 |
| Fase 8: Skills | 5-7 | 🔵 P3 |
| Fase 9: Self-Contained | 7-10 | 🔵 P3 |
| **Total** | **46-64 días (~9-13 semanas)** | |
