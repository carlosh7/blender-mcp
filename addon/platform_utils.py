"""
blender-mcp — Cross-platform utilities (inside Blender)
Duplicated from src/blender_mcp/platform.py for ZIP self-containment.
"""
import os
import sys
from pathlib import Path

SYSTEM = sys.platform  # 'win32', 'darwin', 'linux'

def _is_windows(): return SYSTEM == "win32"
def _is_mac(): return SYSTEM == "darwin"
def _is_linux(): return SYSTEM.startswith("linux")


def get_config_dir() -> Path:
    if _is_windows():
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif _is_mac():
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path.home() / ".config"
    return base / "blender-mcp"


def get_log_dir() -> Path:
    d = get_config_dir() / "logs"
    d.mkdir(parents=True, exist_ok=True)
    return d


def get_opencode_auth_path() -> Path:
    if _is_windows():
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif _is_mac():
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path.home() / ".local" / "share"
    return base / "opencode" / "auth.json"


def get_opencode_config_paths() -> list[Path]:
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
