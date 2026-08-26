#!/usr/bin/env python3
"""Sesión host: Blender headless con addon blender-mcp-ultra + socket :9876.

Uso (desde la raíz del repo):
    blender -b --factory-startup --python scripts/host_session.py

Carga .host/session.blend si existe (estado persistente de este host) y
registra el addon con el socket MCP activo en localhost:9876.
"""

import os
import sys
import traceback

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

import bpy  # noqa: E402

SESSION = os.path.join(REPO, ".host", "session.blend")
if os.path.exists(SESSION):
    bpy.ops.wm.open_mainfile(filepath=SESSION)
    print(f"[host] sesión cargada: {SESSION}", flush=True)

try:
    import addon

    addon.register()
    from addon import _axsock

    srv = _axsock._socket_server
    print(f"[host] socket listening={srv.listening} host={srv.host}:{srv.port}", flush=True)
except Exception:
    traceback.print_exc()
    raise SystemExit(1)

print("[host] READY", flush=True)
