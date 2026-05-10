#!/usr/bin/env python3
"""
install.py — Universal blender-mcp addon installer for Windows, Linux, macOS.
Auto-detects Blender version and installs the addon.
"""

import os
import sys
import shutil
import platform
import subprocess
import json
from pathlib import Path

SYSTEM = platform.system()
ADDON_SRC = Path(__file__).parent / "addon"


def find_blender_version() -> str | None:
    """Detect installed Blender version."""
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
    """Return the Blender addons directory for the detected version."""
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
    print(f"\n  blender-mcp — Addon Installer ({SYSTEM})\n")

    # Check source
    if not ADDON_SRC.exists():
        print(f"  ❌ Addon source not found: {ADDON_SRC}")
        print(f"     Run this script from the blender-mcp root directory.")
        sys.exit(1)

    # Detect Blender
    version = find_blender_version()
    if not version:
        print(f"  ❌ Blender not found.")
        if SYSTEM == "Windows":
            print(f"     Download from: https://www.blender.org/download/")
        elif SYSTEM == "Linux":
            print(f"     Install: sudo apt install blender")
        sys.exit(1)

    addon_dir = get_addon_dir(version)
    if not addon_dir:
        print(f"  ❌ Could not determine addon directory for Blender {version}")
        sys.exit(1)

    # Install
    os.makedirs(addon_dir, exist_ok=True)
    for item in ADDON_SRC.iterdir():
        dst = addon_dir / item.name
        if item.is_dir():
            shutil.copytree(item, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(item, dst)

    print(f"  ✅ Addon installed!")
    print(f"     Location: {addon_dir}")
    print(f"     Blender:  {version}")
    print()
    print(f"     Next steps:")
    print(f"     1. Open Blender")
    print(f"     2. Edit → Preferences → Add-ons")
    print(f"     3. Search for 'AI Assistant'")
    print(f"     4. Enable it")
    print(f"     5. In 3D Viewport, press N → AI tab")
    print()


if __name__ == "__main__":
    install()
