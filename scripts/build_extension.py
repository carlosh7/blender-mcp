#!/usr/bin/env python3
"""Construir el .zip de la extensión de Blender (4.2+) desde addon/.

Uso: python scripts/build_extension.py [--out dist]
El zip resultante se instala con: Blender → Preferences → Add-ons → Install.
"""

import argparse
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ADDON = REPO / "addon"

INCLUDE = [
    "*.py",
    "blender_manifest.toml",
    "operators/*.py",
    "panels/*.py",
    "core/**/*.py",
    "organic/*.py",
    "perception/*.py",
    "server/*.py",
    "libraries/*.py",
    "handlers/*.py",
    "ai/*.py",
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(REPO / "dist"))
    args = ap.parse_args()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not (ADDON / "blender_manifest.toml").exists():
        print("ERROR: falta addon/blender_manifest.toml", file=sys.stderr)
        return 1

    zip_path = out_dir / "blender_mcp_ultra.zip"
    n = 0
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for pattern in INCLUDE:
            for f in sorted(ADDON.glob(pattern)):
                if not f.is_file() or "__pycache__" in f.parts:
                    continue
                zf.write(f, arcname=str(f.relative_to(ADDON)))
                n += 1
    print(f"OK: {zip_path} ({n} archivos)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
