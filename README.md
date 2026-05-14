# blender-mcp v0.8.31

> **El sistema MCP para Blender más completo.** Arrastra el ZIP a Blender y escribe "crea un cubo rojo". Funciona con **cualquier cliente**: opencode, Claude Desktop, Cursor, Antigravity, VS Code, Windsurf, LM Studio, Ollama...

---

## ✨ Capacidades (82 tools)

| Categoría | Tools | Descripción |
|-----------|-------|-------------|
| **Escena** | 10 | Info, captura, limpieza, análisis |
| **Objetos** | 5 | Crear, mover, duplicar, eliminar |
| **Materiales** | 5 | PBR, colores, nodos shader |
| **Luces** | 2 | Point/Sun/Spot/Area, iluminación 3 puntos |
| **Cámara** | 3 | Crear, apuntar, encuadrar, DOF |
| **Modificadores** | 22 tipos | SubSurf, Bevel, Boolean, Array, Mirror... |
| **Shader Nodes** | 40+ tipos | Árbol completo de nodos |
| **Animación** | 5 | Keyframes, rotar, escalar, acciones |
| **Geometry Nodes** | 5 | Redes, scatter, conexiones |
| **Render** | 5 | Cycles/EEVEE, resolución, GPU/CPU |
| **Import/Export** | 12 formatos | GLB, FBX, OBJ, STL, USD, DAE, PLY... |
| **UV & Texture** | 7 métodos | Unwrap, baking, canales UV |
| **Batch** | 4 | Turntable, rename, delete masivo |
| **Rigging** | 5 | Armaduras, huesos, constraints, auto-weight |
| **Scene Utils** | 6 | Purga, análisis, join, hide |
| **3D Printing** | 5 | Manifold, mm-scale, STL, bed layout |
| **Poly Haven** | 6 | HDRI, texturas, modelos (gratis) |
| **Sketchfab** | 4 | Búsqueda y descarga de modelos |
| **Hyper3D Rodin** | 4 | Generación IA texto→3D |
| **Hunyuan3D** | 4 | Generación IA texto/imagen→3D |
| **AmbientCG** | 3 | Materiales PBR gratis |

---

## 🚀 Instalación — Cero Configuración

**Solo necesitas Blender.** Sin terminal, sin Python, sin uv, sin nada más.

### 1. Descargar
[axiom_engine_v0.8.31.zip](dist/axiom_engine_v0.8.31.zip) — 75KB

### 2. Arrastrar a Blender
Suelta el ZIP en la ventana de Blender → `Edit → Preferences → Add-ons` → busca **"AXIOM"** → activa.

### 3. Escribir
Presiona `N` en el viewport 3D → pestaña **Axiom** → escribe *"crea un cubo rojo"* → Send.

✅ **Sin configuración. Sin API keys. Sin terminal.**

---

## 🔌 Clientes Soportados

El addon **auto-configura** los clientes al activarse. Cada cliente ve las mismas 82 tools.

| Cliente | Cómo se conecta | Auto-config |
|---------|----------------|-------------|
| **opencode** | MCP vía SSE :45677 | ✅ Crea `~/.config/opencode/mcp.json` |
| **Claude Desktop** | MCP vía SSE :45677 | ✅ Crea `~/.config/Claude/claude_desktop_config.json` |
| **Claude Code** | Hereda de Claude Desktop | ✅ Usa la misma config |
| **Cursor** | MCP vía SSE :45677 | ✅ Crea `~/.cursor/mcp.json` |
| **Antigravity** | HTTP REST :9877 | ✅ Servidor HTTP incluido en el addon |
| **VS Code** | MCP STDIO | 📝 Usar `uvx blender-mcp` |
| **Windsurf** | MCP STDIO | 📝 Configurar MCP server |
| **LM Studio** | MCP STDIO | 📝 Native MCP v0.3.0+ |
| **Ollama + Continue** | MCP STDIO | 📝 Configurar Continue |
| **Desde el chat de Blender** | Timer interno | ✅ Procesado por auto_process |

### Ejemplos de uso

**Desde opencode:**
```
Tú: "crea una esfera metálica dorada en Blender"
Yo (agente): usa create_object + create_material + assign_material
```

**Desde Claude Desktop:**
```
User: "Add three-point lighting to the scene and render at 4K"
Claude: llama a setup_three_point_lighting() + set_render_resolution() + render_frame()
```

**Desde Antigravity (HTTP):**
```bash
curl -X POST http://localhost:9877/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "crea un balón rojo"}'
```

**Desde el chat de Blender:**
```
Escribe: "analiza la escena y dime qué tiene más polígonos"
Responde: "El objeto silla tiene 24,500 polígonos..."
```

---

## 🏗️ Arquitectura

```
                         ┌──────────────────────────┐
                         │       BLENDER ADDON       │
                         │  (único archivo: ZIP)     │
                         │                           │
                         │  addon/server/             │
                         │  ├── MCP SSE :45677       │  ← opencode, Claude, Cursor
                         │  └── HTTP REST :9877      │  ← Antigravity, curl
                         │                           │
                         │  addon/handlers/ (22)      │  ← 82 tools
                         │  addon/client/ (4)         │  ← LLM providers
                         │  addon/auto_process.py     │  ← Procesa chat internamente
                         │  addon/auto_config.py      │  ← Auto-configura clientes
                         │  addon/panels/             │  ← UI en Blender
                         └──────────┬────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
               opencode        Claude/Cursor   Antigravity
               (MCP SSE)       (MCP SSE)       (HTTP REST)
```

---

## 📖 Guía Rápida de Tools

| Tool | Para qué | Ejemplo |
|------|----------|---------|
| `create_object(type, name, location)` | Crear cubo/esfera/cilindro/cono/toro | `create_object("SPHERE")` |
| `create_material(name, color, metallic)` | Crear material PBR | `create_material("Oro", [1,0.84,0,1], 1.0)` |
| `add_modifier(object, type)` | 22 modificadores | `add_modifier("Cubo", "bevel")` |
| `setup_three_point_lighting()` | Iluminación profesional automática | `setup_three_point_lighting("Cubo")` |
| `export_scene(filepath, format)` | 12 formatos de exportación | `export_scene("/tmp/mesa.glb")` |
| `search_polyhaven(type, query)` | Buscar texturas/HDRI gratis | `search_polyhaven("textures", "brick")` |
| `animate_location(object, start, end)` | Animación de posición | `animate_location("Sphere", 1, 60)` |
| `check_manifold(object)` | Verificar si es imprimible en 3D | `check_manifold("Pieza")` |
| `execute_blender_code(code)` | Python directo en Blender | `execute_blender_code("bpy.ops.mesh...")` |
| `get_viewport_screenshot()` | Capturar viewport | Validar visualmente |

---

## 📊 Comparativa

| Proyecto | Tools | Assets | Multi-LLM | Modo Autónomo | HTTP API | Auto-config | Spatial | Precio |
|----------|-------|--------|-----------|---------------|----------|-------------|---------|--------|
| **Este proyecto** | **82** | ✅ 5 integraciones | ✅ 7 proveedores | ✅ Sí | ✅ Sí | ✅ Sí | ✅ Sí | **Gratis** |
| ahujasid/blender-mcp | ~30 | ✅ PH+SK+HR+HY | ❌ Solo Claude | ❌ No | ❌ No | ❌ No | ❌ No | Gratis |
| youichi-uda/mcp-pro | 120+ | ✅ PH+SK | ❌ Solo Claude | ❌ No | ❌ No | ❌ No | ❌ No | $15 |
| Blender.org oficial | ~10 | ❌ No | ❌ Solo Claude | ❌ No | ❌ No | ❌ No | ❌ No | Gratis |
| GenesisCore | ~20 | ✅ PH | ✅ 7 proveedores | ⚠️ Parcial | ❌ No | ❌ No | ❌ No | Gratis |

---

## 🧩 Integraciones

| Servicio | API Key | Gratis | Qué ofrece |
|----------|---------|--------|------------|
| **Poly Haven** | No | ✅ Sí | HDRI, texturas PBR, modelos 3D |
| **Sketchfab** | Sí | ❌ | Modelos realistas descargables |
| **Hyper3D Rodin** | Free Trial | ⚠️ Limitado | Generación IA texto→3D |
| **Hunyuan3D** | Sí | ❌ | Generación IA texto/imagen→3D |
| **AmbientCG** | No | ✅ Sí | Materiales PBR (gratis, sin key) |

---

## 📁 Documentación

| Documento | Contenido |
|-----------|-----------|
| [GUIDE.md](GUIDE.md) | Guía completa paso a paso de todas las tools |
| [ROADMAP.md](ROADMAP.md) | Plan de desarrollo |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Diagrama de arquitectura |
| [docs/claude-desktop.md](docs/claude-desktop.md) | Configurar Claude Desktop |
| [docs/cursor.md](docs/cursor.md) | Configurar Cursor |
| [docs/vscode.md](docs/vscode.md) | Configurar VS Code |
| [docs/opencode.md](docs/opencode.md) | Configurar opencode |
| [docs/antigravity.md](docs/antigravity.md) | Configurar Antigravity |
| [docs/local-llm.md](docs/local-llm.md) | Ollama, LM Studio, Continue |
| [docs/remote.md](docs/remote.md) | Docker y remoto |

---

## ⚖️ Licencia

MIT — Ver [LICENSE](LICENSE)
