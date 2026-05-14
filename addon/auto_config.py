"""
auto_config.py — Auto-configura clientes MCP externos.
Crea/configura los archivos necesarios para que cada cliente
encuentre el servidor MCP embebido de blender-mCP.

Clientes soportados:
  - opencode  → ~/.config/opencode/mcp.json  (formato opencode)
  - Claude Desktop → ~/.config/Claude/claude_desktop_config.json
  - Cursor    → ~/.cursor/mcp.json

NO toca opencode.json principal (para no romper proveedores/modelos).
"""
import bpy
import os
import json
import sys
from pathlib import Path

from .platform_utils import _is_windows, _is_mac


def start():
    creados = []
    if _config_opencode():
        creados.append("opencode")
    if _config_claude():
        creados.append("Claude Desktop")
    if _config_cursor():
        creados.append("Cursor")
    if creados:
        print(f"[blender-mcp] ✅ Auto-config: {', '.join(creados)}")
    print("[blender-mcp] 📡 HTTP REST API en http://localhost:9877/")


def _server_url():
    return "http://localhost:45677/sse"


# ─── Rutas opencode ───
def _opencode_dir():
    if _is_windows():
        return Path(os.environ.get("APPDATA", "")) / "opencode"
    elif _is_mac():
        return Path.home() / "Library" / "Application Support" / "opencode"
    else:
        return Path.home() / ".config" / "opencode"


def _bridge_path():
    """Ruta absoluta al STDIO bridge dentro del addon instalado."""
    return str(Path(__file__).parent / "stdio_bridge.py")


def _stdio_config():
    """Config STDIO estándar para cualquier cliente MCP."""
    return {
        "type": "local",
        "command": [sys.executable, _bridge_path()],
        "enabled": True,
    }


def _config_opencode():
    """Escribe configuración STDIO solo en mcp.json (no toca opencode.json)."""
    d = _opencode_dir()
    d.mkdir(parents=True, exist_ok=True)
    cfg = _stdio_config()

    # Solo mcp.json — no tocar opencode.json (tiene modelo/proveedores)
    path = d / "mcp.json"
    data = {}
    if path.exists():
        try:
            data = json.loads(path.read_text())
        except:
            pass
    if not isinstance(data, dict):
        data = {}
    data.setdefault("mcp", {})
    data["mcp"]["blender"] = cfg
    path.write_text(json.dumps(data, indent=2))

    return True


# ─── Claude Desktop ───
def _claude_config_dir():
    if _is_windows():
        return Path(os.environ.get("APPDATA", "")) / "Claude"
    elif _is_mac():
        return Path.home() / "Library" / "Application Support" / "Claude"
    else:
        return Path.home() / ".config" / "Claude"


def _config_claude():
    """Crea/actualiza claude_desktop_config.json."""
    config_dir = _claude_config_dir()
    if not config_dir.exists():
        return False
    path = config_dir / "claude_desktop_config.json"
    data = {}
    if path.exists():
        try:
            data = json.loads(path.read_text())
        except:
            pass
    data.setdefault("mcpServers", {})
    data["mcpServers"]["blender"] = {
        "type": "sse",
        "url": _server_url(),
    }
    path.write_text(json.dumps(data, indent=2))
    return True


# ─── Cursor ───
def _config_cursor():
    """Crea/actualiza .cursor/mcp.json."""
    path = Path.home() / ".cursor" / "mcp.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {}
    if path.exists():
        try:
            data = json.loads(path.read_text())
        except:
            pass
    data.setdefault("mcpServers", {})
    data["mcpServers"]["blender"] = {
        "type": "sse",
        "url": _server_url(),
    }
    path.write_text(json.dumps(data, indent=2))
    return True
