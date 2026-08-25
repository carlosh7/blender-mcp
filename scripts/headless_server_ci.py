"""Servidor socket headless para CI: blender -b --python scripts/headless_server_ci.py

No retorna; atiende clientes de forma síncrona en el hilo principal.
Puerto configurable via env BLENDER_MCP_PORT (default 9876).
"""

import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "addon"))
sys.path.insert(0, str(REPO))

import _axsock  # noqa: E402

_port = int(os.environ.get("BLENDER_MCP_PORT", "9876"))
print(f"[CI] levantando servidor headless en :{_port}", flush=True)
_axsock.serve_forever(port=_port)
