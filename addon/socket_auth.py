"""
socket_auth.py — Token del socket y carga del code_guard.

El token es OBLIGATORIO: env BLENDER_MCP_TOKEN > propiedad de escena >
auto-generado y persistido en <config>/blender-mcp/socket_token (0600),
compartido con el gateway (blender_connection.get_socket_token).
Sin bpy directo: la lectura de escena es lazy (importable fuera de Blender).
"""

import os
import secrets
from pathlib import Path

_token_cache = None


def token_file_path() -> Path:
    """Ruta del token compartido con el gateway (misma fórmula cross-OS)."""
    import sys

    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path.home() / ".config"
    return base / "blender-mcp" / "socket_token"


def load_or_create_token() -> str:
    """Lee (o genera y persiste) el token del socket para este usuario."""
    try:
        p = token_file_path()
        if p.exists():
            t = p.read_text(encoding="utf-8").strip()
            if t:
                return t
        t = secrets.token_hex(16)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(t, encoding="utf-8")
        try:
            os.chmod(p, 0o600)
        except Exception:
            pass
        return t
    except Exception:
        return ""


def resolve_token(env_var: str = "BLENDER_MCP_TOKEN", scene_prop: str = "mcp_ultra_socket_token"):
    """Orden de resolución del token (con cache)."""
    global _token_cache
    if _token_cache is not None:
        return _token_cache
    token = os.environ.get(env_var, "")
    if not token:
        try:
            import bpy

            token = bpy.context.scene.get(scene_prop, "") or ""
        except Exception:
            token = ""
    if not token:
        token = load_or_create_token()
    _token_cache = token
    return token


def load_code_guard():
    """Carga code_guard.py (mismo directorio): blocklist AST para execute_code."""
    import importlib.util

    guard_path = Path(__file__).resolve().parent / "code_guard.py"
    if not guard_path.exists():
        return None
    try:
        spec = importlib.util.spec_from_file_location("bmcp_addon_code_guard", guard_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception:
        return None
