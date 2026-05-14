"""
auto_config.py — Auto-configura clientes MCP externos (opencode, Claude Desktop, Cursor)
Al activar el addon, escribe archivos de config apuntando al servidor MCP embebido :45677.
Solo escribe si el cliente está instalado y el archivo no existe (no sobreescribe).
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
    else:
        print("[blender-mcp] Auto-config: ningún cliente externo detectado")
    print("[blender-mcp] 📡 Antigravity: HTTP API en http://localhost:9877/api/")


def _server_url():
    return "http://localhost:45677/sse"


def _get_opencode_paths():
    """Devuelve rutas de config de opencode según SO."""
    paths = []
    if _is_windows():
        appdata = Path(os.environ.get("APPDATA", ""))
        if appdata:
            paths.append(appdata / "opencode" / "opencode.json")
    elif _is_mac():
        paths.append(Path.home() / "Library" / "Application Support" / "opencode" / "opencode.json")
    else:
        paths.append(Path.home() / ".config" / "opencode" / "opencode.json")
    return paths


def _config_opencode():
    """Escribe config para opencode (solo si no existe)."""
    for config_path in _get_opencode_paths():
        if config_path.exists():
            return False  # Ya existe, no sobreescribir
        config_dir = config_path.parent
        if not config_dir.exists():
            continue  # opencode no instalado
        config_dir.mkdir(parents=True, exist_ok=True)
        config_path.write_text(json.dumps({
            "mcpServers": {
                "blender": {
                    "type": "sse",
                    "url": _server_url(),
                }
            }
        }, indent=2))
        return True
    return False


def _config_claude():
    """Escribe config para Claude Desktop (solo si instalado y no existe)."""
    if _is_windows():
        config_dir = Path(os.environ.get("APPDATA", "")) / "Claude"
    elif _is_mac():
        config_dir = Path.home() / "Library" / "Application Support" / "Claude"
    else:
        config_dir = Path.home() / ".config" / "Claude"

    if not config_dir.exists():
        return False
    config_path = config_dir / "claude_desktop_config.json"
    if config_path.exists():
        return False
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps({
        "mcpServers": {
            "blender": {
                "command": sys.executable,
                "args": ["-c", "import addon.server; addon.server.start_embedded_server()"],
                "url": _server_url(),
            }
        }
    }, indent=2))
    return True


def _config_cursor():
    """Escribe .cursor/mcp.json global (solo si no existe)."""
    config_path = Path.home() / ".cursor" / "mcp.json"
    if config_path.exists():
        return False
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps({
        "mcpServers": {
            "blender": {
                "type": "sse",
                "url": _server_url(),
            }
        }
    }, indent=2))
    return True
