"""
blender-mcp — Cross-platform utilities (inside Blender)
Duplicated from src/blender_mcp/platform.py for ZIP self-containment.
"""
import os
import platform
from pathlib import Path

SYSTEM = platform.system()


def get_config_dir() -> Path:
    if SYSTEM == "Windows":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif SYSTEM == "Darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path.home() / ".config"
    return base / "blender-mcp"


def get_log_dir() -> Path:
    d = get_config_dir() / "logs"
    d.mkdir(parents=True, exist_ok=True)
    return d


def get_opencode_auth_path() -> Path:
    if SYSTEM == "Windows":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif SYSTEM == "Darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path.home() / ".local" / "share"
    return base / "opencode" / "auth.json"


def get_opencode_config_paths() -> list[Path]:
    paths = []
    if SYSTEM == "Windows":
        appdata = Path(os.environ.get("APPDATA", ""))
        if appdata:
            paths.append(appdata / "opencode" / "opencode.json")
    elif SYSTEM == "Darwin":
        paths.append(Path.home() / "Library" / "Application Support" / "opencode" / "opencode.json")
    else:
        paths.append(Path.home() / ".config" / "opencode" / "opencode.json")
    return paths
