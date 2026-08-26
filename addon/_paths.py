"""Rutas temporales cross-OS para el addon (Windows/macOS/Linux).

Reemplaza los antiguos '/tmp/...' hardcodeados:
- Linux:   /tmp/<name>
- macOS:   /var/folders/.../T/<name>
- Windows: %TEMP%\\<name>
"""

import tempfile
from pathlib import Path


def temp_dir(name: str = "") -> Path:
    """Devuelve el directorio temporal base/name, creándolo si no existe."""
    base = Path(tempfile.gettempdir()) / name
    base.mkdir(parents=True, exist_ok=True)
    return base
