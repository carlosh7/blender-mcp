#!/usr/bin/env python3
"""Descarga la documentación RST de Blender (data/api, data/manual).

Uso:
    python scripts/fetch_docs_data.py [--url URL] [--dest data]

Por defecto usa el release asset del proyecto. Si el asset no está
disponible aún, se puede apuntar a un tar.gz propio con --url o
DATA_DOCS_URL. Estructura esperada del tarball: api/*.rst, manual/*.
"""

import argparse
import os
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DEFAULT_URL = "https://github.com/carlosh7/blender-mcp/releases/download/docs/api_docs.tar.gz"


def docs_installed(dest: Path) -> bool:
    api = dest / "api"
    return api.exists() and len(list(api.glob("*.rst"))) > 10


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--url", default=os.getenv("DATA_DOCS_URL", DEFAULT_URL))
    ap.add_argument("--dest", default=str(REPO / "data"))
    args = ap.parse_args()

    dest = Path(args.dest)
    if docs_installed(dest):
        print(f"✅ data/ ya presente en {dest} — nada que hacer")
        return 0

    print(f"⬇️  Descargando {args.url} ...")
    try:
        with urllib.request.urlopen(args.url, timeout=120) as resp:  # noqa: S310
            payload = resp.read()
    except Exception as e:
        print(f"❌ No se pudo descargar: {e}")
        print("   La búsqueda de docs (search_api_docs) quedará degradada;")
        print("   el resto del proyecto funciona igual. Sube el tarball al")
        print("   release 'docs' del repo o pasa --url con un tar.gz válido.")
        return 1

    dest.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tmp:
        tmp.write(payload)
        tmp_path = tmp.name
    try:
        with tarfile.open(tmp_path, "r:gz") as tar:
            tar.extractall(dest)  # noqa: S202
    finally:
        os.unlink(tmp_path)

    if docs_installed(dest):
        print(f"✅ Documentación instalada en {dest}")
        return 0
    print("⚠️  Tarball extraído pero no contiene api/*.rst — revisa la estructura")
    return 1


if __name__ == "__main__":
    sys.exit(main())
