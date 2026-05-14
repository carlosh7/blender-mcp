# blender-mcp Architecture

> Arquitectura objetivo del sistema MCP para Blender más completo del ecosistema.

---

## Diagrama General

```
                          ┌──────────────────────────────────────────────────────────┐
                          │                   CLIENTES MCP                          │
                          │                                                          │
                          │  ┌──────────┐  ┌────────┐  ┌──────────┐  ┌───────────┐ │
                          │  │  Claude   │  │ Cursor │  │ opencode │  │ Antigravity│ │
                          │  │  Desktop  │  │        │  │          │  │ (HTTP RST) │ │
                          │  └─────┬────┘  └───┬────┘  └────┬─────┘  └──────┬────┘ │
                          │        │           │            │               │      │
                          │        │    ┌──────┴──────┐     │               │      │
                          │        │    │ VS Code     │     │               │      │
                          │        │    │ Copilot Chat│     │               │      │
                          │        │    └──────┬──────┘     │               │      │
                          │        │           │            │               │      │
                          │        └─────┬─────┘            │               │      │
                          │              │                  │               │      │
                          └──────────────┼──────────────────┼───────────────┼──────┘
                                         │                  │               │
                                   STDIO │             SSE  │          HTTP │
                                         │                  │               │
                    ┌────────────────────┼──────────────────┼───────────────┼────────┐
                    │                    ▼                  ▼               ▼        │
                    │          ┌─────────────────────────────────────────────────┐   │
                    │          │           MCP SERVER LAYER                      │   │
                    │          │  ┌──────────────────────────────────────────┐   │   │
                    │          │  │  src/blender_mcp/server.py (FastMCP)     │   │   │
                    │          │  │                                          │   │   │
                    │          │  │  ┌──────────────────────────────────┐    │   │   │
                    │          │  │  │  RESOURCES (blender://)         │    │   │   │
                    │          │  │  │  ├─ /scene/info                 │    │   │   │
                    │          │  │  │  ├─ /scene/objects              │    │   │   │
                    │          │  │  │  ├─ /scene/materials            │    │   │   │
                    │          │  │  │  └─ /scene/active-object        │    │   │   │
                    │          │  │  └──────────────────────────────────┘    │   │   │
                    │          │  │                                          │   │   │
                    │          │  │  ┌──────────────────────────────────┐    │   │   │
                    │          │  │  │  TOOLS (categorías modulares)    │    │   │   │
                    │          │  │  │  ├─ tools/scene.py              │    │   │   │
                    │          │  │  │  ├─ tools/objects.py            │    │   │   │
                    │          │  │  │  ├─ tools/materials.py          │    │   │   │
                    │          │  │  │  ├─ tools/modifiers.py          │    │   │   │
                    │          │  │  │  ├─ tools/animation.py          │    │   │   │
                    │          │  │  │  ├─ tools/geometry_nodes.py     │    │   │   │
                    │          │  │  │  ├─ tools/lights.py             │    │   │   │
                    │          │  │  │  ├─ tools/camera.py             │    │   │   │
                    │          │  │  │  ├─ tools/render.py             │    │   │   │
                    │          │  │  │  ├─ tools/io.py                 │    │   │   │
                    │          │  │  │  ├─ tools/uv_texture.py         │    │   │   │
                    │          │  │  │  ├─ tools/shader_nodes.py       │    │   │   │
                    │          │  │  │  ├─ tools/rigging.py            │    │   │   │
                    │          │  │  │  ├─ tools/printing.py           │    │   │   │
                    │          │  │  │  ├─ tools/polyhaven.py          │    │   │   │
                    │          │  │  │  ├─ tools/sketchfab.py          │    │   │   │
                    │          │  │  │  ├─ tools/hyper3d.py            │    │   │   │
                    │          │  │  │  └─ tools/hunyuan.py            │    │   │   │
                    │          │  │  └──────────────────────────────────┘    │   │   │
                    │          │  │                                          │   │   │
                    │          │  │  ┌──────────────────────────────────┐    │   │   │
                    │          │  │  │  PROMPTS (guías para LLM)        │    │   │   │
                    │          │  │  │  ├─ asset_creation_strategy()    │    │   │   │
                    │          │  │  │  ├─ scene_analysis_strategy()    │    │   │   │
                    │          │  │  │  └─ geometry_nodes_document()    │    │   │   │
                    │          │  │  └──────────────────────────────────┘    │   │   │
                    │          │  └──────────────────────────────────────────┘   │   │
                    │          │                                                   │   │
                    │          │  ┌──────────────────────────────────────────┐   │   │
                    │          │  │  AGENTE AUTÓNOMO (modo embebido)        │   │   │
                    │          │  │  src/blender_mcp/agent/                 │   │   │
                    │          │  │  ├─ host.py        ← Loop agente       │   │   │
                    │          │  │  ├─ memory.py      ← Persistencia      │   │   │
                    │          │  │  └─ providers.py   ← LLM providers      │   │   │
                    │          │  └──────────────────────────────────────────┘   │   │
                    │          │                                                   │   │
                    │          │  ┌──────────────────────────────────────────┐   │   │
                    │          │  │  PROXY (modo externo)                    │   │   │
                    │          │  │  src/blender_mcp/proxy.py               │   │   │
                    │          │  └──────────────────────────────────────────┘   │   │
                    │          └─────────────────────────────────────────────────┘   │
                    │                            │                                   │
                    │                     TCP Socket (9876)                          │
                    │                            │                                   │
                    │          ┌─────────────────┼─────────────────────────────────┐ │
                    │          │                 ▼                                 │ │
                    │          │    BLENDER ADDON (addon/)                         │ │
                    │          │                                                   │ │
                    │          │  ┌──────────────────────────────────────────┐    │ │
                    │          │  │  Socket Server (blender_socket.py)       │    │ │
                    │          │  │  Escucha en :9876, recibe comandos       │    │ │
                    │          │  │  Despacha a handlers por tipo            │    │ │
                    │          │  └──────────────────────────────────────────┘    │ │
                    │          │            │                                     │ │
                    │          │            ▼                                     │ │
                    │          │  ┌──────────────────────────────────────────┐    │ │
                    │          │  │  Handlers (addon/handlers/)              │    │ │
                    │          │  │  ┌──────────────────────────────────┐    │    │ │
                    │          │  │  │  scene.py    objects.py          │    │    │ │
                    │          │  │  │  materials.py shader_nodes.py    │    │    │ │
                    │          │  │  │  lights.py   modifiers.py        │    │    │ │
                    │          │  │  │  animation.py  geometry_nodes.py │    │    │ │
                    │          │  │  │  camera.py   render.py           │    │    │ │
                    │          │  │  │  io.py       uv_texture.py       │    │    │ │
                    │          │  │  │  rigging.py  printing.py         │    │    │ │
                    │          │  │  │  polyhaven.py sketchfab.py       │    │    │ │
                    │          │  │  │  hyper3d.py  hunyuan.py          │    │    │ │
                    │          │  │  └──────────────────────────────────┘    │    │ │
                    │          │  └──────────────────────────────────────────┘    │ │
                    │          │            │                                     │ │
                    │          │            ▼                                     │ │
                    │          │  ┌──────────────────────────────────────────┐    │ │
                    │          │  │  Módulos existentes (Axiom Engine)       │    │ │
                    │          │  │  ├─ assembly.py   ← Assembly engine      │    │ │
                    │          │  │  ├─ scanner.py    ← Geometry scanner     │    │ │
                    │          │  │  └─ spatial.py    ← Spatial validator    │    │ │
                    │          │  └──────────────────────────────────────────┘    │ │
                    │          │                                                   │ │
                    │          │  ┌──────────────────────────────────────────┐    │ │
                    │          │  │  Paneles UI (addon/panels/)              │    │ │
                    │          │  │  ├─ chat.py       ← Chat principal      │    │ │
                    │          │  │  ├─ integrations.py ← Toggles assets    │    │ │
                    │          │  │  └─ config.py     ← Config proveedores  │    │ │
                    │          │  └──────────────────────────────────────────┘    │ │
                    │          │                                                   │ │
                    │          │  ┌──────────────────────────────────────────┐    │ │
                    │          │  │  MCP Embebido (Fase 9, opcional)        │    │ │
                    │          │  │  ├─ client/     ← LLM providers locals  │    │ │
                    │          │  │  └─ server/     ← FastMCP interno       │    │ │
                    │          │  └──────────────────────────────────────────┘    │ │
                    │          └─────────────────────────────────────────────────┘ │
                    │                                                              │
                    │  ┌──────────────────────────────────────────────────────────┐│
                    │  │  HTTP BRIDGE (para Antigravity y REST)                   ││
                    │  │  http_bridge.py — Puerto 9877                            ││
                    │  │  Endpoints: /api/health, /api/chat, /api/generate, etc.  ││
                    │  └──────────────────────────────────────────────────────────┘│
                    └──────────────────────────────────────────────────────────────┘
```

---

## Flujo de Datos por Modo

### Modo Proxy (Rápido — con Claude Desktop/Cursor)

```
Usuario → [Blender Panel] → msg → [Socket] → [MCP Server]
  → tool call → [Claude Desktop] → LLM decide
  → tool call → [MCP Server] → [Blender Addon] → resultado
  → Claude piensa → otra tool o respuesta final
  → [MCP Server] → [Blender Panel] → usuario ve resultado
```

✅ Rápido porque Claude maneja el loop de herramientas externamente
✅ Sin consumo de API keys propias (usa las de Claude)

### Modo Autónomo (Lento pero sin dependencias externas)

```
Usuario → [Blender Panel] → msg → [Socket] → [MCP Server]
  → [Agent Host] → llama a LLM via API key propia
  → LLM responde con tool call(s)
  → [Agent Host] ejecuta tools via socket → [Blender]
  → resultado → LLM de nuevo → loop hasta max_turns
  → respuesta final → [Blender Panel]
```

✅ Funciona sin Claude Desktop
✅ Multi-provider (DeepSeek, Anthropic, OpenRouter, Google...)
❌ Más lento (cada turno = API call + socket round-trip)

---

## Estrategia de Lazy Loading (de youichi-uda)

```
Al inicio:     15 tools core (get_scene_info, execute_code, etc.)
Bajo demanda:  El cliente llama list_tool_categories() → ve 17 categorías
               El cliente llama enable_tools("modifiers") → se activan 22 tools de modifiers
               El cliente llama enable_tools("animation") → se activan 8 tools de animation
```

Esto evita saturar la lista de tools del LLM y mejora la velocidad de descubrimiento.

---

## Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| **MCP Protocol** | `mcp[cli]>=1.3.0` (FastMCP) |
| **Blender API** | `bpy` (nativo en Blender) |
| **Transport STDIO** | MCP estándar |
| **Transport SSE** | `uvicorn` + `sse_starlette` |
| **Transport HTTP** | `http.server` (stdlib) |
| **LLM API Calls** | `urllib.request` (stdlib, sin dependencias extra) |
| **Async** | `asyncio` + `threading` |
| **Streaming** | `httpx` (opcional) o `urllib` chunked |
| **Empaquetado** | `pyproject.toml` + `hatchling` |
| **Cache** | `diskcache` o SQLite |
| **Config** | JSON + env vars |
| **Tests** | `pytest` |

---

## Decisiones de Arquitectura Clave

| Decisión | Opción | Por qué |
|----------|--------|---------|
| FastMCP vs raw MCP | **FastMCP** | Menos boilerplate, type hints automáticos, lifespan, resources, prompts nativos |
| STDIO vs SSE | **Ambos** | STDIO para clientes estándar, SSE para persistencia y conexiones largas |
| Un socket vs múltiples | **Socket único** | Puerto 9876, simplifica firewall, debugging, y estado compartido |
| Handlers modulares vs monolithic addon.py | **Modular** | Inspirado en yuri-schmaltz, facilita testing y contribuciones |
| Agente embebido vs externo | **Ambos (dual-mode)** | El modo externo es rápido, el embebido es autónomo — tener ambos es la ventaja competitiva |
| Cache en disco vs memoria | **Disco + memoria** | Memoria para sesión, disco para assets y config cruzando sesiones |

---

## Puertos

| Puerto | Servicio | Protocolo |
|--------|----------|-----------|
| 9876 | Blender Socket | TCP (JSON) |
| 9877 | HTTP Bridge | REST |
| 9879 | MCP SSE | HTTP+SSE |
| 45677 | MCP Interno (Fase 9) | SSE (self-contained mode) |
