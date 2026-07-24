# Cursor Integration

## Configuration

Add to `.cursor/mcp.json` in your project:

```json
{
  "mcpServers": {
    "blender": {
      "command": "python3",
      "args": ["/path/to/blender-mcp-ultra/mcp_adapter.py"],
      "env": {
        "BLENDER_HOST": "localhost",
        "BLENDER_PORT": "9876"
      }
    }
  }
}
```

Or add globally to `~/.cursor/mcp.json`.

## Usage

1. Start Blender with MCP server:
   ```bash
   blender --background --python start_server.py
   ```

2. Open Cursor

3. Use Cursor's AI to control Blender:
   ```
   @blender Create a character rig
   ```

## Features

- AI-assisted 3D modeling
- Code generation for Blender
- Scene automation

## Troubleshooting

- **Cursor doesn't detect MCP**: Restart Cursor
- **Tool errors**: Check Blender connection
- **Performance issues**: Reduce tool complexity
