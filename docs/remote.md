# Remote / Docker Support

Ejecuta blender-mcp en un servidor remoto o contenedor Docker.

## Variables de entorno para conexión remota

| Variable | Default | Descripción |
|----------|---------|-------------|
| `BLENDER_HOST` | `localhost` | IP del host donde corre Blender |
| `BLENDER_PORT` | `9876` | Puerto del socket de Blender |

## Ejemplo: Blender en un servidor, MCP en otro

```bash
# En el servidor con Blender (IP: 192.168.1.100)
export BLENDER_HOST=0.0.0.0
export BLENDER_PORT=9876
# Inicia el addon en Blender

# En la máquina con el MCP client (Claude/Cursor)
export BLENDER_HOST=192.168.1.100
export BLENDER_PORT=9876
uvx blender-mcp
```

## Docker

```dockerfile
FROM python:3.12-slim

RUN pip install uv
RUN uv tool install blender-mcp

EXPOSE 9876 9877 9879

CMD ["blender-mcp", "--mode", "sse", "--port", "9879"]
```

### docker-compose.yml (ejemplo para headless)

```yaml
version: '3.8'
services:
  blender:
    image: nytimes/blender:latest
    command: blender -b -P /scripts/socket_server.py
    volumes:
      - ./scripts:/scripts
    ports:
      - "9876:9876"

  mcp-server:
    build: .
    depends_on: [blender]
    environment:
      - BLENDER_HOST=blender
      - BLENDER_PORT=9876
    ports:
      - "9877:9877"
      - "9879:9879"
```

## Notas

- Asegúrate de que los puertos 9876, 9877, 9879 estén abiertos en el firewall
- Para conexiones remotas, considera usar SSH tunneling o VPN
- El modo SSE (puerto 9879) es ideal para conexiones remotas persistentes
