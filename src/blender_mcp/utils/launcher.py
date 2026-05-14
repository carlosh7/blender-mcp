"""
blender-mcp — Hybrid Headless Fallback Launcher
Si Blender no está corriendo, lanza blender --background para ejecutar comandos.
"""
import json
import os
import subprocess
import tempfile

_SOCKET_HOST = "localhost"
_SOCKET_PORT = 9876
_BLENDER_PATH_ENV = "BLENDER_PATH"
_TIMEOUT = 120.0


def _get_blender():
    return os.environ.get(_BLENDER_PATH_ENV, "blender")


def _socket_available():
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((_SOCKET_HOST, _SOCKET_PORT))
        s.close()
        return True
    except (ConnectionRefusedError, OSError, socket.timeout):
        return False


def execute(code, blend_file=None):
    """Execute code. Tries socket first, falls back to blender --background."""
    if _socket_available():
        from blender_connection import get_blender
        b = get_blender()
        return b.send_command("execute_code", {"code": code})
    return _run_headless(code, blend_file)


def _run_headless(code, blend_file=None):
    blender = _get_blender()
    wrapper = (
        "import json, sys\n"
        "from contextlib import redirect_stdout, redirect_stderr\n"
        "import io\n"
        "buf = io.StringIO()\n"
        "try:\n"
        "    ns = {}\n"
        "    exec({!r}, ns)\n"
        "    print('OK')\n"
        "except Exception as e:\n"
        "    import traceback\n"
        "    traceback.print_exc()\n"
    ).format(code)

    cmd = [blender, "--background", "--python-expr", wrapper]
    if blend_file:
        cmd.insert(2, blend_file)

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True, text=True, timeout=_TIMEOUT,
        )
        return {"status": "success" if proc.returncode == 0 else "error",
                "output": proc.stdout[:2000], "stderr": proc.stderr[:500]}
    except subprocess.TimeoutExpired:
        return {"status": "error", "output": "Timeout"}
    except FileNotFoundError:
        return {"status": "error", "output": f"Blender not found at '{blender}'"}
