# VS Code Integration

Conecta blender-mcp con [Visual Studio Code](https://code.visualstudio.com/) usando la extensión MCP oficial.

## Requisitos

- VS Code 1.90+
- [GitHub Copilot Chat](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot-chat) (soporta MCP)
- Blender 4.0+ con addon

## Instalación

### 1. Click para instalar

[![Install in VS Code](https://img.shields.io/badge/VS_Code-Install_blender--mcp-0098FF?style=flat-square&logo=visualstudiocode&logoColor=ffffff)](vscode:mcp/install?%7B%22name%22%3A%22blender-mcp%22%2C%22type%22%3A%22stdio%22%2C%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22blender-mcp%22%5D%7D)

### 2. Manual

Abre VS Code → Settings → Extensions → MCP → Add server:

```json
{
    "name": "blender",
    "type": "stdio",
    "command": "uvx",
    "args": ["blender-mcp"]
}
```

### 3. Usar

En VS Code, abre el chat de Copilot y escribe:

> "@blender create a cube and apply a metallic red material"

## Notas

- VS Code GitHub Copilot Chat no soporta `tools/list_changed`. Si agregas tools dinámicamente, reinicia la conexión.
- Para modo eager (cargar todas las tools al inicio): `BLENDER_MCP_PRO_EAGER=1 uvx blender-mcp`
