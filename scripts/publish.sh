#!/usr/bin/env bash
# publish.sh — Publica el paquete en PyPI (wheel + sdist, NO el .zip de la extensión).
# Uso:   bash scripts/publish.sh            (pedirá el API token de PyPI)
#        PYPI_TOKEN=pypi-... bash scripts/publish.sh
set -euo pipefail

cd "$(dirname "$0")/.."

echo "── blender-mcp-ultra → PyPI ──────────────────────────────"

# Artefactos esperados: wheel + sdist de la versión actual del pyproject
VERSION=$(grep -m1 '^version' pyproject.toml | sed 's/.*"\(.*\)".*/\1/')
WHEEL="dist/blender_mcp_ultra-${VERSION}-py3-none-any.whl"
SDIST="dist/blender_mcp_ultra-${VERSION}.tar.gz"

for f in "$WHEEL" "$SDIST"; do
    if [ ! -f "$f" ]; then
        echo "❌ Falta $f — construye primero:  python3 -m pip wheel . -w dist --no-deps && python3 -m build --sdist --outdir dist ."
        exit 1
    fi
done

echo "── 1/2 Validando metadatos…"
python3 -m twine check "$WHEEL" "$SDIST"

echo "── 2/2 Subiendo v${VERSION} (pega tu API token pypi-… cuando lo pida)…"
if [ -n "${PYPI_TOKEN:-}" ]; then
    python3 -m twine upload --username __token__ --password "$PYPI_TOKEN" "$WHEEL" "$SDIST"
else
    python3 -m twine upload --username __token__ --non-interactive "$WHEEL" "$SDIST" \
        || python3 -m twine upload --username __token__ "$WHEEL" "$SDIST"
fi

echo "✅ v${VERSION} publicada. Verifica:  pip index versions blender-mcp-ultra"
