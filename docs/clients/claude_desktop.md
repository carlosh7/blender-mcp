# Claude Desktop Integration

## Configuration

Add to `~/.claude/claude_desktop_config.json`:

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

2. Restart Claude Desktop

3. Ask Claude to control Blender:
   ```
   Create a red cube in Blender
   Set up three-point lighting
   ```

## Features

- Natural language control
- Screenshot capture
- Scene analysis
- Object manipulation

## Troubleshooting

- **Claude doesn't see tools**: Restart Claude Desktop
- **Connection errors**: Check Blender is running
- **Slow responses**: Increase timeout in config
