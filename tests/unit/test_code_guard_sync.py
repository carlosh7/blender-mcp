"""
blender-mcp — code_guard drift test
La implementación canónica vive en addon/code_guard.py (el addon debe ser
autocontenido en el zip de la extensión); blender_mcp/code_guard.py es la
copia que viaja en el wheel para el gateway. Este test impide que diverjan.
"""

import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
_CANONICAL = REPO / "addon" / "code_guard.py"
_WHEEL_COPY = REPO / "blender_mcp" / "code_guard.py"


def test_code_guard_copies_identical():
    assert _CANONICAL.exists() and _WHEEL_COPY.exists()
    assert _CANONICAL.read_bytes() == _WHEEL_COPY.read_bytes(), (
        "addon/code_guard.py y blender_mcp/code_guard.py han divergido: "
        "sincroniza ambas copias (canónica: addon/)"
    )


def test_gateway_loads_code_guard_from_package():
    os.chdir(REPO)
    import importlib
    import sys

    sys.path.insert(0, str(REPO))
    import mcp_server

    importlib.reload(mcp_server)
    assert mcp_server._code_guard is not None, "el gateway no pudo cargar code_guard"
    assert hasattr(mcp_server._code_guard, "check_code")
