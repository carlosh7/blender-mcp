# Cursor Integration

Conecta blender-mcp con [Cursor](https://cursor.com) para controlar Blender desde el editor de código.

## Requisitos

- Cursor 0.45+ con soporte MCP
- Blender 4.0+ con el addon instalado
- Python 3.10+ con `uv`

## Opción 1: Global (recomendado)

En Cursor, ve a **Settings → MCP → Add new global MCP server** y pega:

```json
{
    "name": "blender",
    "command": "uvx",
    "args": ["blender-mcp"]
}
```

## Opción 2: Por proyecto

Crea `.cursor/mcp.json` en la raíz de tu proyecto:

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

## Opción 3: Windows

En Windows, usa `cmd` como command:

```json
{
    "mcpServers": {
        "blender": {
            "command": "cmd",
            "args": ["/c", "uvx", "blender-mcp"]
        }
    }
}
```

## Verificación

1. En Blender: activa el addon y conecta el socket (pestaña Axiom → Connect)
2. En Cursor: abre el panel MCP (icono de enchufe) y verifica que "blender" esté verde
3. Pregunta: "List the objects in the Blender scene"
