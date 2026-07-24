# opencode Integration

## Configuration

Add to `~/.config/opencode/opencode.json`:

```json
{
  "mcp": {
    "blender-mcp-ultra": {
      "command": ["python3", "/path/to/blender-mcp-ultra/mcp_adapter.py"],
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

1. Start Blender with MCP server:
   ```bash
   blender --background --python start_server.py
   ```

2. Restart opencode

3. Use tools:
   ```python
   tool("object.create", {"type": "MESH", "name": "Cube"})
   tool("material.create", {"name": "Red", "color": [1, 0, 0, 1]})
   ```

## Troubleshooting

- **Connection refused**: Check if Blender is running and port 9876 is open
- **No tools available**: Restart opencode after configuration changes
- **Timeout errors**: Increase timeout in configuration
