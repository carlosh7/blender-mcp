"""
blender-mcp — Test Configuration
"""

import os
import sys

import pytest

from helpers import is_blender_available, socket_token

# Add addon to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "addon"))

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ── Aislamiento de escena: snapshot de objetos antes de la suite; al acabar
# se eliminan los creados por tests (headless-safe: sin bpy.context.window).

_existing_objects = None


def _socket_command(command: str, params: dict | None = None) -> dict:
    import json
    import socket

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(60)
    sock.connect(("localhost", 9876))
    cmd = {"command": command, "params": params or {}}
    tok = socket_token()
    if tok:
        cmd["token"] = tok
    sock.sendall(json.dumps(cmd).encode())
    buf = b""
    resp = None
    while True:
        chunk = sock.recv(262144)
        if not chunk:
            break
        buf += chunk
        try:
            resp = json.loads(buf.decode())
            break
        except json.JSONDecodeError:
            continue
    sock.close()
    return resp or {}


@pytest.fixture(scope="session", autouse=True)
def _isolated_blender_scene():
    global _existing_objects
    if not is_blender_available():
        yield
        return
    try:
        resp = _socket_command(
            "execute_code",
            {"code": 'import bpy\nprint("NAMES:" + repr(sorted(o.name for o in bpy.data.objects)))\n'},
        )
        out = (resp.get("result") or {}).get("output", "")
        import ast

        _existing_objects = (
            ast.literal_eval(out.split("NAMES:")[-1].strip())
            if "NAMES:" in out
            else None
        )
    except Exception:
        _existing_objects = None
    yield
    if _existing_objects:
        teardown = (
            "import bpy\n"
            f"existing = {set(_existing_objects)!r}\n"
            "kill = [o for o in bpy.data.objects if o.name not in existing]\n"
            "for o in kill:\n"
            "    bpy.data.objects.remove(o, do_unlink=True)\n"
            "n = bpy.data.orphans_purge()\n"
            'print(f"LIMPIADOS:{len(kill)}|PURGA:{n}")\n'
        )
        try:
            resp = _socket_command("execute_code", {"code": teardown})
            out = (resp.get("result") or {}).get("output", "")
            print(f"\n[conftest] limpieza de escena: {out.strip()}")
        except Exception:
            pass
