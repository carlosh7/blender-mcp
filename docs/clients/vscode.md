# VS Code Integration

## Configuration

Add to `.vscode/mcp.json` in your workspace:

```json
{
  "servers": {
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

2. Open VS Code

3. Use GitHub Copilot Chat:
   ```
   @blender Create a product visualization
   ```

## Features

- GitHub Copilot integration
- Code suggestions for Blender
- Scene automation

## Troubleshooting

- **VS Code doesn't see MCP**: Reload window
- **Copilot errors**: Check MCP configuration
- **Slow responses**: Optimize tool calls
