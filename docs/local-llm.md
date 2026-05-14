# Local LLM Integration (LM Studio, Continue, Ollama)

Conecta blender-mcp con LLMs locales para controlar Blender sin conexión a internet.

## LM Studio

[LM Studio](https://lmstudio.ai/) v0.3.0+ tiene soporte nativo MCP.

1. Abre LM Studio y carga tu modelo local
2. Ve a **Settings → Developer → Model Context Protocol (MCP)**
3. Click **Add MCP server** y configura:

   - **Command**: `uvx`
   - **Arguments**: `blender-mcp`

4. Guarda y abre un chat. Verás las herramientas de Blender disponibles.

## Continue (VS Code / Desktop)

[Continue](https://continue.dev/) es un asistente AI open source que soporta MCP.

1. Instala la extensión Continue en VS Code o usa la desktop app
2. Configura tu modelo local (Ollama, llama.cpp, etc.)
3. En `~/.continue/config.json`, agrega:

```json
{
  "experimental": {
    "mcpServers": {
      "blender": {
        "command": "uvx",
        "args": ["blender-mcp"]
      }
    }
  }
}
```

## Ollama

[Ollama](https://ollama.ai/) + Continue/Open WebUI:

1. Instala Ollama y descarga un modelo:
   ```bash
   ollama pull llama3.2
   ```
2. Usa Continue o cualquier cliente MCP apuntando a Ollama
3. Configura el MCP server como en la sección de Continue

## Open WebUI

[Open WebUI](https://openwebui.com/) soporta conexiones MCP:

1. Configura Open WebUI para usar tu modelo local (Ollama)
2. Agrega blender-mcp como tool externa
3. Conecta y empieza a crear

## Verificación

```bash
# Test que el servidor funciona
uvx blender-mcp --doctor
```
