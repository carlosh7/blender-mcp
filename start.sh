#!/bin/bash
# start.sh — Start blender-mcp MCP server (Linux/Mac)
# Usage: ./start.sh
DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$DIR/.mcp_server.pid"
LOG_FILE="$HOME/.config/blender-mcp/logs/server.log"
mkdir -p "$(dirname "$LOG_FILE")"

# Detener instancia previa si existe
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    kill "$OLD_PID" 2>/dev/null
    rm -f "$PID_FILE"
fi

# Arrancar usando el entry point del paquete (o directo)
if command -v blender-mcp &> /dev/null; then
    nohup blender-mcp start > "$LOG_FILE" 2>&1 &
else
    nohup "$DIR/.venv/bin/python" "$DIR/mcp_server.py" > "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
fi

echo "✅ blender-mcp MCP Server started (log: $LOG_FILE)"
