#!/usr/bin/env python3
"""
install.py — Installer universal addon blender-mcp untuk Windows, Linux, dan macOS.
Mendeteksi versi Blender lalu memasang paket addon kanonik.
"""

import os
import sys
import shutil
import platform
import subprocess
import json
from pathlib import Path

SYSTEM = platform.system()
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def find_blender_version() -> str | None:
    """Deteksi versi Blender yang terpasang."""
    blender = shutil.which("blender.exe") or shutil.which("blender")
    if not blender:
        return None

    try:
        result = subprocess.run([blender, "--version"], capture_output=True, text=True, timeout=10)
        for line in result.stdout.split("\n"):
            if "Blender" in line:
                import re
                m = re.search(r"Blender\s+(\d+\.\d+)", line)
                if m:
                    return m.group(1)
    except:
        pass
    return None


def get_addon_dir(version: str) -> Path | None:
    """Kembalikan direktori addon Blender untuk versi yang terdeteksi."""
    home = Path.home()

    if SYSTEM == "Windows":
        base = Path(os.environ.get("APPDATA", "")) / "Blender Foundation" / f"Blender {version}"
        return base / "scripts" / "addons" / "ai_assistant"

    elif SYSTEM == "Linux":
        return home / ".config" / "blender" / version / "scripts" / "addons" / "ai_assistant"

    elif SYSTEM == "Darwin":
        return home / "Library" / "Application Support" / "Blender" / version / "scripts" / "addons" / "ai_assistant"

    return None


def install():
    print(f"\n  blender-mcp — Installer Addon ({SYSTEM})\n")

    required = ("__init__.py", "addon", "blender_mcp", "mcp_server.py",
                "mcp_tools.py", "blender_connection.py", "data", "src")
    missing = [name for name in required if not (PROJECT_ROOT / name).exists()]
    if missing:
        print(f"  Sumber addon tidak lengkap: {', '.join(missing)}")
        sys.exit(1)

    # Deteksi Blender
    version = find_blender_version()
    if not version:
        print("  Blender tidak ditemukan.")
        if SYSTEM == "Windows":
            print("     Unduh: https://www.blender.org/download/")
        elif SYSTEM == "Linux":
            print("     Pasang: sudo apt install blender")
        sys.exit(1)

    addon_dir = get_addon_dir(version)
    if not addon_dir:
        print(f"  Direktori addon Blender {version} tidak dapat ditentukan")
        sys.exit(1)

    # Pasang paket kanonik: root __init__.py + modul runtime yang dipakainya.
    if addon_dir.exists():
        shutil.rmtree(addon_dir)
    addon_dir.mkdir(parents=True)
    for name in required:
        src = PROJECT_ROOT / name
        dst = addon_dir / name
        if src.is_dir():
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        else:
            shutil.copy2(src, dst)
    manifest = PROJECT_ROOT / "blender_manifest.toml"
    if manifest.exists():
        shutil.copy2(manifest, addon_dir / manifest.name)

    print("  Addon berhasil dipasang.")
    print(f"     Lokasi:  {addon_dir}")
    print(f"     Blender: {version}")
    print()
    print("     Langkah berikutnya:")
    print("     1. Buka Blender")
    print("     2. Edit → Preferences → Add-ons")
    print("     3. Cari 'blender-mcp-ultra'")
    print("     4. Aktifkan addon")
    print("     5. Buka Sidebar (N) → Axiom di 3D Viewport")
    print()


if __name__ == "__main__":
    install()
