# Windsurf Integration

Conecta blender-mcp con [Windsurf](https://codeium.com/windsurf) para controlar Blender desde el IDE AI.

## Requisitos

- Windsurf (última versión)
- Blender 4.0+ con addon
- Python 3.10+ con `uv`

## Configuración

En Windsurf, ve a **Settings → MCP Servers → Add Server**:

```json
{
    "mcpServers": {
        "blender": {
            "command": "uvx",
            "args": ["blender-mcp"]
        }
    }
}
```

## Uso

1. Activa el addon en Blender
2. Conecta el socket (pestaña Axiom → Connect)
3. En Windsurf, usa el asistente AI para controlar Blender:

> "Add a subsurf modifier to the selected object and set the render level to 3"
