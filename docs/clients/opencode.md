# opencode Integration

## Prerequisites

1. Install the gateway (provides the `blender-mcp-server` command):

   ```bash
   pip install blender-mcp-ultra
   ```

2. Install the Blender addon (`blender_mcp_ultra.zip`) and enable it — the
   socket on `:9876` starts automatically (or press **Connect** in the N-panel).

The order does not matter: all 245 tools register even if Blender is closed,
and they work as soon as you open it.

## Configuration

Add to `~/.config/opencode/opencode.json`:

```json
{
  "mcp": {
    "blender-mcp-ultra": {
      "command": ["blender-mcp-server"],
      "enabled": true,
      "environment": {
        "BLENDER_HOST": "localhost",
        "BLENDER_PORT": "9876"
      },
      "timeout": 60000,
      "type": "local"
    }
  }
}
```

If you installed from a repo checkout instead of PyPI:

```json
{
  "mcp": {
    "blender-mcp-ultra": {
      "command": ["python3", "/path/to/blender-mcp/mcp_server.py"],
      "enabled": true,
      "environment": {
        "BLENDER_HOST": "localhost",
        "BLENDER_PORT": "9876"
      },
      "timeout": 60000,
      "type": "local"
    }
  }
}
```

## Usage

1. Restart opencode

2. Ask the agent in natural language:
   ```
   Crea una taza de café con material cerámico PBR y renderízala
   ```

The agent will use tools like `object_create`, `material_pbr`, `render_render`.

## Troubleshooting

- **Connection refused**: Open Blender with the addon enabled; tools reconnect
  automatically once it is up
- **No tools available**: Restart opencode after configuration changes
- **Timeout errors**: Increase timeout in configuration
