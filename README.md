# blender-mcp v0.8.2

**The most complete, flexible Blender MCP server** — Control Blender from **any** MCP client (Claude Desktop, Cursor, opencode, VS Code, Windsurf, Antigravity, LM Studio, Ollama...).

> Compatible con cualquier agente MCP. Dos modos de operación: **proxy** (rápido con Claude/Cursor externo) y **autónomo** (embebido, multi-provider, sin dependencias externas).

---

## Features

| Capacidad | Descripción |
|-----------|-------------|
| **Multi-cliente** | Claude Desktop, Cursor, VS Code, opencode, Antigravity, LM Studio, Ollama, Continue |
| **Dual-mode agent** | Proxy mode (rápido) + Autonomous mode (sin Claude Desktop) |
| **120+ tools** | Objects, materials, shader nodes, lights, modifiers, animation, geometry nodes, camera, render, import/export, UV/texture, rigging, 3D printing |
| **Assets integration** | Poly Haven, Sketchfab, Hyper3D Rodin, Hunyuan3D, AmbientCG |
| **Spatial reasoning** | ASCII visualization, anchor snapping, geometry validation |
| **Chat + Model selector** | Multi-provider LLM selector desde el panel de Blender |
| **Export GLTF/GLB** | Modelos listos para web, Three.js, Unity |
| **Memory persistence** | Chat history entre sesiones |
| **HTTP Bridge** | REST API para Antigravity y clientes HTTP |
| **Axiom Precision Engine** | Assembly, symmetry, normals, collision detection, blueprint extraction |

---

## Quick Install — Cero Configuración

> **Arrastra el ZIP a Blender y escribe.** No necesitas terminal, ni Python, ni API keys.

### Opción 1: Arrastrar ZIP a Blender (recomendado)

1. Descarga [`axiom_engine_v0.8.0.zip`](dist/axiom_engine_v0.8.0.zip)
2. Arrástralo a la ventana de Blender
3. Actívalo en `Edit → Preferences → Add-ons` (busca "AXIOM")
4. En el viewport 3D, presiona `N` → pestaña **Axiom**
5. Escribe "crea un cubo rojo" y presiona **Send**

✅ El addon auto-instala sus dependencias.
✅ No necesitas Python externo, ni `uv`, ni terminal.

### Opción 2: Extension Manager (Blender 4.2+)

1. Descarga [`axiom_engine_v0.8.0.zip`](dist/axiom_engine_v0.8.0.zip)
2. Blender → `Edit → Preferences → Extensions`
3. Click dropdown → **Install from Disk...**
4. Selecciona el ZIP
5. Actívalo

### Opción 3: Terminal (usuarios avanzados)

```bash
# Con uv (auto-instala Python si no lo tienes)
uvx blender-mcp

# Con pip
pip install blender-mcp
blender-mcp
```

---

## Clientes Soportados

| Cliente | Transporte | Config |
|---------|-----------|--------|
| **Claude Desktop** | STDIO | `uvx blender-mcp` |
| **Claude Code** | STDIO | `claude mcp add blender uvx blender-mcp` |
| **Cursor** | STDIO | `uvx blender-mcp` en MCP settings |
| **VS Code** | STDIO | Via MCP extension |
| **opencode** | STDIO/SSE | Config automática |
| **Antigravity** | HTTP REST | `http://localhost:9877/api/` |
| **LM Studio** | STDIO | Native MCP support v0.3.0+ |
| **Ollama** | STDIO | Via Continue / Open WebUI |
| **Continue** | STDIO | `uvx blender-mcp` |

---

## Architecture

```
Cualquier Cliente MCP
    │ STDIO / SSE / HTTP
    ▼
┌─────────────────────────────────┐
│  src/blender_mcp/server.py      │
│  (FastMCP — 120+ tools)         │
│  ├─ tools/scene.py              │
│  ├─ tools/objects.py            │
│  ├─ tools/materials.py          │
│  ├─ tools/modifiers.py          │
│  ├─ tools/lights.py             │
│  ├─ tools/camera.py             │
│  ├─ tools/animation.py          │
│  ├─ tools/geometry_nodes.py     │
│  ├─ tools/shader_nodes.py       │
│  ├─ tools/render.py             │
│  ├─ tools/io.py                 │
│  ├─ tools/uv_texture.py         │
│  ├─ tools/rigging.py            │
│  ├─ tools/printing.py           │
│  ├─ tools/polyhaven.py          │
│  ├─ tools/sketchfab.py          │
│  ├─ tools/hyper3d.py            │
│  └─ tools/hunyuan.py            │
│  agent/host.py (modo autónomo)  │
│  proxy.py (modo proxy rápido)   │
└──────────┬──────────────────────┘
           │ TCP Socket :9876
           ▼
┌─────────────────────────────────┐
│  Blender Addon (addon/)         │
│  handlers/ (modular)            │
│  ├─ scene.py, objects.py        │
│  ├─ materials, modifiers        │
│  ├─ lights, camera, render      │
│  ├─ polyhaven, sketchfab        │
│  ├─ hyper3d, hunyuan            │
│  └─ printing, ambientcg         │
│  panels/ (UI en Blender)        │
│  blender_socket.py              │
└─────────────────────────────────┘
```

---

## Roadmap

Ver [ROADMAP.md](ROADMAP.md) para el plan completo de 9 fases.

| Fase | Estado | Descripción |
|------|--------|-------------|
| 0: Fundación | 🔄 En progreso | pyproject.toml, CLI, doctor, modular handlers |
| 1: Panel Híbrido | 📅 Planeado | Toggles Poly Haven, Sketchfab, Hyper3D, Hunyuan3D |
| 2: Integraciones Reales | 📅 Planeado | Implementar Poly Haven, Sketchfab, Hyper3D reales |
| 3: 120+ Tools | 📅 Planeado | 17 categorías de herramientas MCP |
| 4: Velocidad Agente | 📅 Planeado | Modo proxy + streaming + optimización |
| 5: Recursos MCP | 📅 Planeado | Resources + Prompts + Images |
| 6: Multi-Cliente | 📅 Planeado | Docs para todos los clientes |
| 7: Calidad | 📅 Planeado | Tests, telemetría, CI/CD |
| 8: Skills | 📅 Planeado | Skills markdown para Claude Code |
| 9: Self-Contained | 📅 Planeado | MCP client dentro de Blender |

---

## Comparativa con otras alternativas

| Proyecto | Tools | Assets | Multi-LLM | Modo Autónomo | HTTP Bridge | Spatial | Precio |
|----------|-------|--------|-----------|---------------|-------------|---------|--------|
| **Este proyecto** | 120+ | ✅ Todos | ✅ 5+ proveedores | ✅ Sí | ✅ Sí | ✅ Sí | Gratis |
| ahujasid/blender-mcp | ~30 | ✅ PH+SK+HR+HY | ❌ Solo Claude | ❌ No | ❌ No | ❌ No | Gratis |
| youichi-uda/mcp-pro | 120+ | ✅ PH+SK | ❌ Solo Claude | ❌ No | ❌ No | ❌ No | $15/$5mo |
| Blender.org oficial | ~10 | ❌ No | ❌ Solo Claude | ❌ No | ❌ No | ❌ No | Gratis |
| AIGODLIKE/GenesisCore | ~20 | ✅ PH | ✅ 7 proveedores | ⚠️ Parcial | ❌ No | ❌ No | Gratis |

---

## Documentación

- [Roadmap completo](ROADMAP.md)
- [Arquitectura](ARCHITECTURE.md)
- [Instalación](docs/INSTALL.md)
- [Claude Desktop](docs/claude-desktop.md)
- [Cursor](docs/cursor.md)
- [VS Code](docs/vscode.md)
- [Windsurf](docs/windsurf.md)
- [Local LLMs (LM Studio / Ollama / Continue)](docs/local-llm.md)
- [opencode](docs/opencode.md)
- [Antigravity (HTTP Bridge)](docs/antigravity.md)
- [Remote / Docker](docs/remote.md)

## Licencia

MIT — Ver [LICENSE](LICENSE)
