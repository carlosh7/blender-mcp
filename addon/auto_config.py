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


# ─── opencode ───
def _opencode_path():
    """Ruta del archivo principal de opencode."""
    if _is_windows():
        base = Path(os.environ.get("APPDATA", ""))
    elif _is_mac():
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path.home() / ".config"
    return base / "opencode" / "opencode.json"


def _config_opencode():
    """Agrega blender al opencode.json principal (sección mcp)."""
    path = _opencode_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {"$schema": "https://opencode.ai/config.json"}
    if path.exists():
        try:
            existing = json.loads(path.read_text())
            data = existing if isinstance(existing, dict) else data
        except:
            pass
    data.setdefault("mcp", {})
    data["mcp"]["blender"] = {
        "type": "sse",
        "url": _server_url(),
        "enabled": True,
    }
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
