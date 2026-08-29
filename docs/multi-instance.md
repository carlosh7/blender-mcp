# Multi-instancia de Blender

Cada instancia de Blender sirve su propio socket; cada gateway (y por tanto
cada cliente MCP) apunta a la que quiera. Útil para modelar mientras otra
instancia renderiza, o para aislar proyectos.

## 1. Arrancar instancias en puertos distintos

```bash
# Instancia A (puerto por defecto 9876)
blender proyecto_a.blend --python-expr "from bl_ext.user_default.blender_mcp_ultra import _axsock; _axsock.serve_forever()"

# Instancia B (otro puerto)
BLENDER_MCP_SOCKET_PORT=9877 blender proyecto_b.blend --python-expr "from bl_ext.user_default.blender_mcp_ultra import _axsock; _axsock.serve_forever()"
```

También por código: `_axsock.serve_forever(port=9877)`.

## 2. Conectar un gateway a cada instancia

```bash
BLENDER_PORT=9876 python mcp_server.py   # cliente 1
BLENDER_PORT=9877 python mcp_server.py   # cliente 2
```

En el config del cliente MCP, declara el env por servidor:

```json
{
  "mcpServers": {
    "blender-a": {"command": "blender-mcp-server"},
    "blender-b": {"command": "blender-mcp-server", "env": {"BLENDER_PORT": "9877"}}
  }
}
```

## Notas

- El **token es compartido** (archivo por usuario): las dos instancias lo
  aceptan — son del mismo usuario/host.
- Los puertos se bind **sin** `SO_REUSEPORT`: no puede haber secuestro de
  tráfico entre instancias; un puerto ocupado falla ruidosamente.
- El lock de escena (`scene_lock`) es por instancia: no sincroniza entre
  instancias (cada una tiene su propia escena, no hace falta).
