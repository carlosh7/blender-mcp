# Blender MCP (Model Context Protocol) — Investigacion Completa

> Fecha: 2026-05-10
> Proposito: Recopilacion de repositorios, foros y recursos sobre la integracion de MCP con Blender 3D

---

## 1. ¿Que es MCP?

**MCP (Model Context Protocol)** es un protocolo estandar abierto desarrollado por Anthropic que permite a modelos de lenguaje (LLMs) comunicarse con herramientas externas. En el contexto de Blender, permite que asistentes de IA controlen Blender directamente: crear objetos, aplicar materiales, modificar escenas, renderizar, etc.

El flujo tipico es:

```
Cliente MCP (Claude, Cursor, etc.) → Servidor MCP (blender-mcp) → Addon en Blender → bpy (API de Blender)
```

---

## 2. Repositorio Principal

### ahujasid/blender-mcp

| Atributo | Detalle |
|----------|---------|
| **URL** | https://github.com/ahujasid/blender-mcp |
| **Estrellas** | ⭐ 21,500 |
| **Forks** | 2,100 |
| **Lenguaje** | Python 100% |
| **Licencia** | MIT |
| **Commits** | 139 |
| **Issues** | 44 abiertas |
| **Pull Requests** | 36 abiertos |
| **Ultima actualizacion** | 2026 |

#### Descripcion

BlenderMCP conecta Blender con Claude AI a traves del Model Context Protocol (MCP), permitiendo que Claude interactue directamente con Blender y lo controle. La integracion permite modelado 3D asistido por voz/texto, creacion de escenas y manipulacion.

**Creador:** Siddharth (https://x.com/sidahuj)

#### Caracteristicas

- Comunicacion bidireccional entre Claude AI y Blender via socket
- Creacion, modificacion y eliminacion de objetos 3D
- Control de materiales y colores
- Inspeccion de escenas (informacion detallada)
- Ejecucion de codigo Python arbitrario en Blender
- Descarga de assets de **Poly Haven** (modelos, texturas, HDRIs)
- Descarga de modelos de **Sketchfab**
- Generacion de modelos 3D via **Hyper3D Rodin**
- Soporte para **Hunyuan3D**
- Capturas de pantalla del viewport (feedback visual al asistente)
- Soporte para ejecucion remota

#### Componentes

1. **Blender Addon (`addon.py`)**: Crea un servidor socket dentro de Blender para recibir y ejecutar comandos
2. **MCP Server (`src/blender_mcp/server.py`)**: Servidor Python que implementa MCP y se conecta al addon de Blender

#### Instalacion

**Requisitos:** Blender 3.0+, Python 3.10+, uv

```bash
# 1. Instalar uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Configurar en Claude Desktop (claude_desktop_config.json):
# {
#   "mcpServers": {
#     "blender": {
#       "command": "uvx",
#       "args": ["blender-mcp"]
#     }
#   }
# }

# 3. Descargar addon.py del repo
# 4. Blender > Edit > Preferences > Add-ons > Install > seleccionar addon.py
# 5. Habilitar "Interface: Blender MCP"
# 6. En Blender: sidebar > pestaña BlenderMCP > "Connect to Claude"
```

#### Ejemplos de comandos

- "Create a low poly scene in a dungeon, with a dragon guarding a pot of gold"
- "Create a beach vibe using HDRIs, textures, and models from Poly Haven"
- "Make this car red and metallic"
- "Create a sphere and place it above the cube"
- "Point the camera at the scene, and make it isometric"

#### Integraciones disponibles

| Cliente | Configuracion |
|---------|---------------|
| **Claude Desktop** | `claude_desktop_config.json` con `uvx blender-mcp` |
| **Claude Code** | `claude mcp add blender uvx blender-mcp` |
| **Cursor** | Settings > MCP > add server: `uvx blender-mcp` |
| **VS Code** | Via MCP extension |
| **LM Studio** | v0.3.0+ con soporte MCP nativo |
| **Continue** | Extension VS Code / desktop con configuracion MCP |
| **Ollama** | Via Continue u Open WebUI como cliente |

#### Discord de la comunidad

- **URL:** https://discord.gg/z5apgR8TFU
- Activo, para feedback, soporte y showcases

---

## 3. Fork / Prototipo Relacionado

### yuri-schmaltz/mcp-blender

| Atributo | Detalle |
|----------|---------|
| **URL** | https://github.com/yuri-schmaltz/mcp-blender |
| **Estrellas** | ⭐ 1 |
| **Forks** | 1 |
| **Lenguaje** | Python 100% |
| **Licencia** | MIT |
| **Commits** | 255 |
| **Version** | v2.4.1 (ultimo release) |
| **Ultima actualizacion** | Abr 2026 |

#### Descripcion

"Prototipo para um servidor MPC para integracao do Blender 3D com LLMs locais" — en portugues. Es un fork/derivado con mejoras significativas respecto al original:

#### Caracteristicas adicionales vs original

- **Arquitectura modular**: Handlers separados de `addon.py` para mejor mantenibilidad
- **3D Printing Toolkit**: Dimensiones exactas, espesor de impresion, layout automatico de cama
- **Mesh Integrity**: Verificacion manifold en tiempo real y auto-reparacion
- **AmbientCG Integration**: Busqueda y descarga de miles de materiales PBR
- **Product Studio**: Iluminacion profesional, fondos y camaras automaticas para render de producto
- **Vehicle Rigging**: Rigs automaticos para chasis y ruedas
- **Extension Mode**: Compatible con sistema de Extensiones de Blender 4.2+
- **Interfaz grafica (PySide6)**: Ventana GUI para configurar variables de entorno
- **Health Check**: Comando `--doctor` para diagnosticar la conexion
- **Local Setup buttons**: Botones en el panel de Blender para instalar dependencias, copiar config, abrir logs
- **Logging configurable**: Niveles de log (DEBUG, INFO, WARNING), formato, handler (consola/archivo)
- **Soporte para Poly Haven, Sketchfab y AmbientCG**
- **Pruebas**: Tests E2E, unitarios, GUI y regresion visual

#### Instalacion

```bash
uvx blender-mcp  # mismo comando que el original
# Con GUI:
uv pip install '.[gui]'
uv run blender-mcp-gui
```

---

## 4. Repositorios Alternativos en GitHub

### 4.1 AIGODLIKE/GenesisCore

| Atributo | Detalle |
|----------|---------|
| **URL** | https://github.com/AIGODLIKE/GenesisCore |
| **Estrellas** | ⭐ 118 |
| **Lenguaje** | Python |
| **Temas** | blender, mcp, blender-mcp |

**Descripcion:** Herramienta BlenderMCP que soporta DeepSeek, Claude y otros LLMs. Instalacion con un solo click, completamente integrado en Blender.

---

### 4.2 3DSceneAgent/Vibe3DScene

| Atributo | Detalle |
|----------|---------|
| **URL** | https://github.com/3DSceneAgent/Vibe3DScene |
| **Estrellas** | ⭐ 81 |
| **Lenguaje** | Python |
| **Temas** | agent, blender, mcp, 3d-modeling, langgraph |

**Descripcion:** Crea escenas 3D completas usando solo palabras. Integra LangGraph para el flujo de agente. Actualizado Abr 2026.

---

### 4.3 youichi-uda/blender-mcp-pro

| Atributo | Detalle |
|----------|---------|
| **URL** | https://github.com/youichi-uda/blender-mcp-pro |
| **Estrellas** | ⭐ 15 |
| **Lenguaje** | Python |
| **Temas** | ai, blender, mcp, cursor, claude, windsurf |

**Descripcion:** Servidor MCP con mas de 100 herramientas para Blender. Control de luces, modificadores, animacion, shader nodes, geometry nodes y mas desde Claude, Cursor o Windsurf.

---

### 4.4 xhiroga/blender-mcp-senpai

| Atributo | Detalle |
|----------|---------|
| **URL** | https://github.com/xhiroga/blender-mcp-senpai |
| **Estrellas** | ⭐ 8 |
| **Temas** | blender, mcp, blender-addon |

**Descripcion:** Addon MCP para Blender con enfoque educativo ("senpai").

---

### 4.5 Vertiiii/blender-mcp

| Atributo | Detalle |
|----------|---------|
| **URL** | https://github.com/Vertiiii/blender-mcp |
| **Estrellas** | ⭐ 5 |
| **Lenguaje** | Python |
| **Ultima actualizacion** | May 2026 |

**Descripcion:** Conecta Blender con Claude AI para modelado 3D usando MCP. Soporta Gemini API y Google Generative AI.

---

### 4.6 jithinolickal/blender

| Atributo | Detalle |
|----------|---------|
| **URL** | https://github.com/jithinolickal/blender |
| **Estrellas** | ⭐ 2 |
| **Lenguaje** | Python |
| **Temas** | plugin, blender, mcp, claude, chatgpt, codex |

**Descripcion:** Agent skill para Claude Code, Codex y ChatGPT para diseno 3D en Blender via MCP.

---

### 4.7 RobLe3/cc-blender-skill

| Atributo | Detalle |
|----------|---------|
| **URL** | https://github.com/RobLe3/cc-blender-skill |
| **Estrellas** | ⭐ 1 |
| **Lenguaje** | Python |
| **Ultima actualizacion** | May 2026 |

**Descripcion:** Claude Code skill plugin: maneja Blender 5.x como un artista 3D senior via lenguaje natural. 10 skills encadenables (modelado, materiales, iluminacion, camaras, render, animacion, exportacion, wireframe-to-3d, pro-workflow). Validado en 6 clases de escenas.

---

### 4.8 pradhankubicurrent/pipeline-kit

| Atributo | Detalle |
|----------|---------|
| **URL** | https://github.com/pradhankubicurrent/pipeline-kit |
| **Estrellas** | ⭐ 0 |
| **Lenguaje** | TypeScript + Rust + React |

**Descripcion:** Pipelines de produccion orquestados por IA para Blender. Escribe un brief, obtienes una escena renderizada via DAGs planificados por LLM.

---

### 4.9 ThanhNguyxnOrg/blendops

| Atributo | Detalle |
|----------|---------|
| **URL** | https://github.com/ThanhNguyxnOrg/blendops |
| **Estrellas** | ⭐ 0 |
| **Lenguaje** | JavaScript |
| **Ultima actualizacion** | May 2026 |

**Descripcion:** Workflow y skill pack para no-usuarios de Blender, construido sobre el Blender MCP oficial.

---

### 4.10 mailman242/MpcBlender y mailman242/mpc-blender

| Atributo | Detalle |
|----------|---------|
| **URL 1** | https://github.com/mailman242/MpcBlender |
| **URL 2** | https://github.com/mailman242/mpc-blender |
| **Estrellas** | ⭐ 0 (ambos) |
| **Estado** | El primero es un template vacio de Streamlit; el segundo esta completamente vacio |

**Nota:** Estos repos no tienen contenido util. Ignorar.

---

## 5. Tabla Comparativa

| Repositorio | Estrellas | Forks | Lenguaje | Ultimo commit | Estado |
|-------------|-----------|-------|----------|---------------|--------|
| ahujasid/blender-mcp | 21,500 | 2,100 | Python | 2026 | **Activo** |
| yuri-schmaltz/mcp-blender | 1 | 1 | Python | Abr 2026 | **Activo** (fork con extras) |
| AIGODLIKE/GenesisCore | 118 | - | Python | Abr 2025 | Activo |
| 3DSceneAgent/Vibe3DScene | 81 | - | Python | Abr 2026 | Activo |
| youichi-uda/blender-mcp-pro | 15 | - | Python | Abr 2026 | Activo |
| xhiroga/blender-mcp-senpai | 8 | - | Python | Sep 2025 | Inactivo |
| Vertiiii/blender-mcp | 5 | - | Python | May 2026 | Activo |
| jithinolickal/blender | 2 | - | Python | Mar 2026 | Activo |
| RobLe3/cc-blender-skill | 1 | - | Python | May 2026 | Activo |
| pradhankubicurrent/pipeline-kit | 0 | - | TS/Rust | May 2026 | Nuevo |
| ThanhNguyxnOrg/blendops | 0 | - | JS | May 2026 | Nuevo |
| mailman242/MpcBlender | 0 | 0 | Python | Nov 2025 | **Vacio** |
| mailman242/mpc-blender | 0 | 0 | - | Nov 2025 | **Vacio** |

---

## 6. Foros y Comunidad

| Recurso | URL | Descripcion |
|---------|-----|-------------|
| **Discord (oficial)** | https://discord.gg/z5apgR8TFU | Comunidad principal de blender-mcp |
| **GitHub Discussions** | https://github.com/ahujasid/blender-mcp/discussions | Foro integrado en el repo principal |
| **YouTube - Tutorial completo** | https://www.youtube.com/watch?v=lCyQ717DuzQ | Tutorial de instalacion y uso |
| **Blender Artists** | https://blenderartists.org | Foro general de Blender (sin seccion especifica MCP) |
| **Reddit r/BlenderMCP** | No encontrado oficial | Buscar en Reddit |

---

## 7. Tutoriales en Video

| Video | URL | Descripcion |
|-------|-----|-------------|
| Setup completo | https://www.youtube.com/watch?v=lCyQ717DuzQ | Instalacion y configuracion paso a paso |
| Setup en Cursor | https://www.youtube.com/watch?v=wgWsJshecac | Integracion con Cursor |
| Config Claude Desktop | https://www.youtube.com/watch?v=neoK_WMq92g | Configuracion en Claude Desktop |
| Demo: mazmorra dragon | https://www.youtube.com/watch?v=DqgKuLYUv00 | Escena low poly dungeon |
| Demo: playa Poly Haven | https://www.youtube.com/watch?v=I29rn92gkC4 | Texturas y HDRIs |
| Demo: imagen a 3D | https://www.youtube.com/watch?v=FDRb03XPiRo | Referencia a escena |
| Demo: ThreeJS desde Blender | https://www.youtube.com/watch?v=jxbNI5L7AH8 | Escena a threejs |

---

## 8. Veredicto / Recomendacion

| Si quieres... | Usa... |
|---------------|--------|
| El mas estable y popular | **ahujasid/blender-mcp** (21.5k ⭐) |
| Caracteristicas avanzadas (3D printing, GUI, health check) | **yuri-schmaltz/mcp-blender** (fork v2.4.1) |
| 100+ herramientas especializadas | **youichi-uda/blender-mcp-pro** |
| Usar DeepSeek u otros LLMs no-Claude | **AIGODLIKE/GenesisCore** |
| Crear escenas con lenguaje natural simple | **3DSceneAgent/Vibe3DScene** |
| Skill para Claude Code | **RobLe3/cc-blender-skill** o **jithinolickal/blender** |

**Recomendacion general:** Comienza con `ahujasid/blender-mcp` por su comunidad masiva y soporte. Si necesitas features extra como GUI, 3D printing toolkit o mejor manejo de errores, migra al fork de `yuri-schmaltz/mcp-blender`.

---

## 9. Protocolo de Comunicacion (detalle tecnico)

El sistema usa JSON sobre TCP sockets:

```json
// Comando enviado al addon
{
  "type": "create_object",
  "params": {
    "type": "CUBE",
    "location": [0, 0, 0],
    "scale": [1, 1, 1]
  }
}

// Respuesta del addon
{
  "status": "ok",
  "result": {
    "name": "Cube",
    "location": [0, 0, 0]
  }
}
```

Puerto por defecto: **9876**
Host por defecto: **localhost**

Variables de entorno:
- `BLENDER_HOST` — host del socket (default: localhost)
- `BLENDER_PORT` — puerto del socket (default: 9876)
- `BLENDER_MCP_LOG_LEVEL` — DEBUG, INFO, WARNING (default: INFO)
- `BLENDER_MCP_LOG_FORMAT` — formato del log
- `BLENDER_MCP_LOG_HANDLER` — console o file
- `BLENDER_MCP_LOG_FILE` — ruta del archivo de log
- `DISABLE_TELEMETRY` — true para desactivar telemetria
