#!/usr/bin/env bash
# Arranque persistente de blender-mcp-ultra en este host.
# 1) Blender headless con el addon (socket :9876)
# 2) Gateway MCP (stdio/SSE) leyendo del registry
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
BLENDER_BIN="${BLENDER_BIN:-$HOME/.local/opt/blender/blender}"

cd "$REPO"
[ -x "$BLENDER_BIN" ] || { echo "Blender no encontrado en $BLENDER_BIN"; exit 1; }

# 1) Blender headless (segundo plano, log persistente)
"$BLENDER_BIN" -b --factory-startup --python scripts/host_session.py \
    > "$REPO/.host/blender.log" 2>&1 &
BLENDER_PID=$!

# esperar socket :9876
for i in $(seq 1 30); do
    nc -z localhost 9876 && break || sleep 1
done
nc -z localhost 9876 || { echo "socket 9876 no respondió"; cat "$REPO/.host/blender.log"; exit 1; }
echo "[start] Blender OK (pid $BLENDER_PID, log .host/blender.log)"

# 2) Gateway MCP en primer plano (Ctrl+C para parar)
exec "$REPO/.venv/bin/python" "$REPO/mcp_server.py"
