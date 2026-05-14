# blender-mcp — Agent Knowledge

## Project structure
```
src/blender_mcp/     → Paquete Python instalable (server, tools, agent, cli)
addon/               → Addon de Blender (handlers, panels, operators, socket)
  handlers/          → Handlers modulares de comandos socket (scene, objects, materials, etc.)
  panels/            → Paneles UI (chat, integrations, config)
  operators/         → Operadores Blender (connect, send, capture, export, setup)
http_bridge.py       → REST API para Antigravity (puerto 9877)
```

## Conventions
- Handler modules in `addon/handlers/` expose `cmd_*()` static methods
- Tool modules in `src/blender_mcp/tools/` register `@mcp.tool()` with FastMCP
- Socket protocol: JSON via TCP port 9876, format `{"type": "...", "params": {...}}`
- Use `bpy.app.timers` for Blender main-thread operations
- Blender addon properties use prefix `blendermcp_` or `aimcp_`

## Key files
| File | Purpose |
|------|---------|
| `src/blender_mcp/server.py` | MCP Server principal (FastMCP) |
| `addon/blender_socket.py` | Socket server dentro de Blender |
| `addon/handlers/base.py` | Base class for handlers |
| `src/blender_mcp/cli.py` | Entry point CLI |
| `src/blender_mcp/agent/host.py` | Agente autónomo multi-provider |

## Targets
- Blender 4.2+ (target), 4.0+ (compat)
- Python 3.10+
- Cualquier cliente MCP (Claude, Cursor, opencode, etc.)
