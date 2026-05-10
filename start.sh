#!/bin/bash
# start.sh — Start blender-mcp HTTP bridge server
# Run this before opening Blender to connect the addon.
# Kill with: ./stop.sh
DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$DIR/.http_bridge.pid"

if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        echo "HTTP bridge already running (PID $OLD_PID)"
        echo "Restart? Run: ./stop.sh && ./start.sh"
        exit 0
    fi
fi

nohup "$DIR/.venv/bin/python3" -c "
import sys, os, signal
sys.path.insert(0, '$DIR')
from http_bridge import start_http_server
os.chdir('$DIR')
server = start_http_server(9877)
print('HTTP bridge ready', flush=True)
signal.pause()
" > "$DIR/http_bridge.log" 2>&1 &

echo $! > "$PID_FILE"
echo "✅ blender-mcp HTTP bridge started (PID $(cat $PID_FILE))"
echo "   Log: $DIR/http_bridge.log"
echo "   Test: curl http://localhost:9877/api/health"
