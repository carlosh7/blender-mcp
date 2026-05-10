#!/bin/bash
# stop.sh — Stop blender-mcp HTTP bridge server
DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$DIR/.http_bridge.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    kill "$PID" 2>/dev/null && echo "✅ Stopped (PID $PID)" || echo "⚠️ Process $PID not found"
    rm -f "$PID_FILE"
else
    echo "No PID file found. Trying pkill..."
    pkill -f "http_bridge" 2>/dev/null && echo "✅ Stopped" || echo "No process found"
fi
