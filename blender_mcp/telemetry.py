"""
blender-mcp — Anonymous Telemetry
Records minimal usage data (tool names, success/failure, duration).
Can be disabled via DISABLE_TELEMETRY env var or Blender preferences.
"""
import json
import os
import time
import threading
import logging
from pathlib import Path

logger = logging.getLogger("blender-mcp")

TELEMETRY_DIR = Path.home() / ".config" / "blender-mcp" / "telemetry"
SESSION_ID = str(int(time.time()))
_event_queue = []
_queue_lock = threading.Lock()
_flush_timer = None

DISABLED = os.environ.get("DISABLE_TELEMETRY", "").lower() in ("true", "1", "yes")


def _ensure_dir():
    TELEMETRY_DIR.mkdir(parents=True, exist_ok=True)


def record(event_name: str, **kwargs):
    """Record a telemetry event (thread-safe)."""
    if DISABLED:
        return
    event = {
        "event": event_name,
        "session": SESSION_ID,
        "ts": time.time(),
        **kwargs,
    }
    with _queue_lock:
        _event_queue.append(event)
    _schedule_flush()


def _schedule_flush():
    global _flush_timer
    if _flush_timer is None:
        _flush_timer = threading.Timer(30.0, _flush)
        _flush_timer.daemon = True
        _flush_timer.start()


def _flush():
    global _flush_timer
    _flush_timer = None
    with _queue_lock:
        if not _event_queue:
            return
        events = list(_event_queue)
        _event_queue.clear()
    try:
        _ensure_dir()
        logfile = TELEMETRY_DIR / f"events_{SESSION_ID}.jsonl"
        with open(logfile, "a") as f:
            for e in events:
                f.write(json.dumps(e) + "\n")
    except Exception as e:
        logger.debug(f"Telemetry flush error: {e}")


def record_tool(tool_name: str, success: bool, duration_ms: float, error: str = ""):
    """Record a tool execution event."""
    kwargs = {"tool": tool_name, "success": success, "duration_ms": round(duration_ms, 1)}
    if error:
        kwargs["error"] = error[:100]
    record("tool_execution", **kwargs)


def record_startup():
    """Record server startup event."""
    record("server_startup", version="0.8.0")
