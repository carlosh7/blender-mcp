#!/bin/bash
# stop.sh — Stop blender-mcp MCP server (Linux/Mac)
# Usage: ./stop.sh
DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$DIR/.mcp_server.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    kill "$PID" 2>/dev/null && echo "✅ Stopped (PID $PID)" || echo "⚠️  Process $PID not found"
    rm -f "$PID_FILE"
else
    # Fallback: buscar proceso
    PID=$(pgrep -f "mcp_server.py" 2>/dev/null | head -1)
    if [ -n "$PID" ]; then
        kill "$PID" 2>/dev/null && echo "✅ Stopped (PID $PID)"
    else
        echo "ℹ️  No server running"
    fi
fi
