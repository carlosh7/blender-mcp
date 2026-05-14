# Claude Desktop Integration

Conecta blender-mcp con Claude Desktop para controlar Blender desde lenguaje natural.

## Requisitos

- Claude Desktop ([descargar](https://claude.ai/download))
- Blender 4.0+ con el addon instalado y el socket corriendo
- Python 3.10+ con `uv` instalado

## Instalación

### 1. Instalar uv (si no lo tienes)

```bash
# Linux / Mac
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows PowerShell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Configurar Claude Desktop

Abre Claude Desktop → Settings (⚙️) → Developer → Edit Config

Agrega esto a `claude_desktop_config.json`:

```json
{
    "mcpServers": {
        "blender": {
            "command": "uvx",
            "args": ["blender-mcp"],
            "env": {}
        }
    }
}
```

**O usando la ruta local** (si tienes el repo clonado):

```json
{
    "mcpServers": {
        "blender": {
            "command": "python3",
            "args": ["/ruta/completa/a/blender-mcp/mcp_server.py"]
        }
    }
}
```

### 3. Iniciar el addon en Blender

1. Abre Blender
2. Activa el addon "AXIOM Precision Engine" en Edit → Preferences → Add-ons
3. En el viewport 3D, presiona `N` para abrir el sidebar
4. Ve a la pestaña **Axiom** → **Connect**
5. Verás "Online" en el panel

### 4. Usar

En Claude Desktop, escribe algo como:

> "Create a red sphere on top of a blue cube with a three-point lighting setup"

Claude usará las herramientas MCP de blender-mcp automáticamente.

## Solución de problemas

| Problema | Solución |
|----------|----------|
| "Could not connect to Blender" | Asegúrate de que el addon esté activo y el socket conectado en Blender |
| uvx no encontrado | Asegúrate de que `uv` esté en el PATH (`which uv`) |
| El addon no aparece | Verifica que la versión de Blender sea 4.0+ |
