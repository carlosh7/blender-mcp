# Windsurf Integration

## Configuration

Add to Windsurf MCP settings:

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

## Usage

1. Start Blender with MCP server:
   ```bash
   blender --background --python start_server.py
   ```

2. Open Windsurf

3. Use Windsurf AI to control Blender:
   ```
   Create an architectural visualization
   ```

## Features

- AI-assisted 3D creation
- Natural language commands
- Scene automation

## Troubleshooting

- **Windsurf doesn't detect MCP**: Restart Windsurf
- **Connection issues**: Verify Blender is running
- **Tool errors**: Check logs
