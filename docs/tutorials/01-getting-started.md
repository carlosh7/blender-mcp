# Video Tutorial: Getting Started with blender-mcp-ultra

## Duration: 5 minutes

## Script

### Intro (0:00 - 0:30)
"Welcome to blender-mcp-ultra! In this tutorial, I'll show you how to control Blender from any AI assistant using MCP."

### Installation (0:30 - 1:30)
1. Show Blender 5.2 LTS
2. Navigate to Edit > Preferences > Add-ons
3. Click "Install..." and select the addon folder
4. Enable "blender-mcp-ultra"
5. Show the MCP panel in 3D Viewport

### MCP Server Setup (1:30 - 2:30)
1. Enable the addon in Blender — the socket on port 9876 starts automatically
2. Install the gateway: `pip install blender-mcp-ultra` (command `blender-mcp-server`)
3. Verify connection with the ping test

### opencode Configuration (2:30 - 3:30)
1. Open opencode config
2. Add blender-mcp-ultra MCP server
3. Restart opencode
4. Verify tools are available

### First Commands (3:30 - 4:30)
1. Create a cube: `tool("object.create", {"type": "MESH", "name": "Cube"})`
2. Create material: `tool("material.create", {"name": "Red", "color": [1,0,0,1]})`
3. Assign material: `tool("material.assign", {"object_name": "Cube", "material_name": "Red"})`
4. Add lighting: `tool("light.three_point", {})`

### Outro (4:30 - 5:00)
"Now you know how to use blender-mcp-ultra! Check out our other tutorials for advanced features."

## Visual Notes
- Screen recording of Blender
- Terminal output
- opencode interface
- Split screen showing Blender + opencode
