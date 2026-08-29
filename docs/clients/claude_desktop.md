# Claude Desktop Integration

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

Add to `~/.claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "blender": {
      "command": "blender-mcp-server"
    }
  }
}
```

If you installed from a repo checkout instead of PyPI:

```json
{
  "mcpServers": {
    "blender": {
      "command": "python3",
      "args": ["/path/to/blender-mcp/mcp_server.py"],
      "env": {
        "BLENDER_HOST": "localhost",
        "BLENDER_PORT": "9876"
      }
    }
  }
}
```

## Usage

1. Restart Claude Desktop

2. Ask Claude to control Blender (open Blender first, or at any point after):
   ```
   Create a red cube in Blender
   Set up three-point lighting
   ```

## Features

- 245 tools: modeling, PBR materials, lighting, physics, render, export…
- Natural language control
- Scene analysis and validation

## Troubleshooting

- **Claude doesn't see tools**: Restart Claude Desktop
- **Connection errors**: Open Blender with the addon enabled; tools reconnect
  automatically once it is up
- **`blender-mcp-server` not found**: use the full path of the executable in
  your virtual environment, or the repo-checkout variant above
