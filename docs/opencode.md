# opencode Integration

Conecta blender-mcp con [opencode](https://opencode.ai) para controlar Blender desde la terminal.

## Requisitos

- opencode instalado ([guía](https://opencode.ai/docs))
- Blender 4.0+ con addon
- Python 3.10+

## Configuración STDIO

Copia `opencode_example.json` a tu config de opencode:

```bash
cp opencode_example.json ~/.config/opencode/mcp.json
```

Ajusta la ruta en `~/.config/opencode/mcp.json`:

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

## Configuración global (recomendada)

Copia `global_opencode.json.example` a la config global:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "blender": {
      "type": "local",
      "command": ["python3", "/ruta/blender-mcp/mcp_server.py"],
      "enabled": true,
      "timeout": 120000
    }
  }
}
```

## Modo SSE (persistente)

Para mantener el servidor corriendo:

```bash
# Iniciar servidor SSE
./start.sh

# El servidor corre en http://localhost:9879/sse
```

Luego configura opencode para conectar via SSE.

## Uso

En el chat de opencode:

> "crea una silla alrededor de la mesa existente"

## Variables de entorno

| Variable | Default | Descripción |
|----------|---------|-------------|
| `BLENDER_HOST` | `localhost` | Host del socket de Blender |
| `BLENDER_PORT` | `9876` | Puerto del socket de Blender |
| `DISABLE_TELEMETRY` | `false` | Desactivar telemetría |
