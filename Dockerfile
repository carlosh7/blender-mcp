# blender-mcp — Gateway MCP remoto (SSE :9879)
#
# El addon de Blender corre en el host (necesita GUI/socket :9876);
# este contenedor expone el gateway MCP para clientes remotos
# (Claude Desktop, Cursor, opencode, etc.) vía SSE.
#
# Build:  docker build -t blender-mcp-gateway .
# Run:    docker run -p 9879:9879 blender-mcp-gateway
# Nota:   el gateway necesita alcanzar el socket de Blender (:9876);
#         usa --network host en Linux o apunta BLENDER_HOST al host.
FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
COPY addon ./addon
COPY blender_mcp ./blender_mcp
COPY mcp_server.py mcp_adapter.py blender_connection.py config.py ./

RUN pip install --no-cache-dir . && pip install --no-cache-dir "mcp[cli]>=1.3.0,<2"

ENV PYTHONUNBUFFERED=1
# SSE accesible fuera del contenedor (docker run -p 9879:9879)
ENV MCP_SSE_HOST=0.0.0.0
ENV MCP_SSE_PORT=9879
EXPOSE 9879

# Transporte SSE para acceso remoto (stdio no aplica en contenedor)
CMD ["python", "mcp_server.py", "--sse"]
