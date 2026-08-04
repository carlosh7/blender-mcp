#!/bin/bash
# install.sh — Install blender-mcp addon for Blender (Linux)
# Detects Blender version and copies addon files to the correct directory.

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Find Blender version
BLENDER_BIN=$(which blender 2>/dev/null || echo "/usr/bin/blender")
if [ ! -f "$BLENDER_BIN" ]; then
    echo "❌ Blender not found. Install it first: sudo apt install blender"
    exit 1
fi

BLENDER_VER=$("$BLENDER_BIN" --version 2>/dev/null | grep -oP 'Blender \K[0-9]+\.[0-9]+' | head -1)
if [ -z "$BLENDER_VER" ]; then
    echo "❌ Could not detect Blender version"
    exit 1
fi

ADDON_DIR="$HOME/.config/blender/$BLENDER_VER/scripts/addons/ai_assistant"

if [ ! -f "$PROJECT_ROOT/__init__.py" ] || [ ! -d "$PROJECT_ROOT/addon" ]; then
    echo "Sumber addon kanonik tidak lengkap: $PROJECT_ROOT"
    exit 1
fi

rm -rf "$ADDON_DIR"
mkdir -p "$ADDON_DIR"
cp "$PROJECT_ROOT/__init__.py" "$PROJECT_ROOT/mcp_server.py" \
   "$PROJECT_ROOT/mcp_tools.py" "$PROJECT_ROOT/blender_connection.py" \
   "$PROJECT_ROOT/blender_manifest.toml" "$ADDON_DIR/"
cp -r "$PROJECT_ROOT/addon" "$PROJECT_ROOT/blender_mcp" \
      "$PROJECT_ROOT/data" "$PROJECT_ROOT/src" "$ADDON_DIR/"
echo "✅ blender-mcp addon installed!"
echo "   Location: $ADDON_DIR"
echo "   Blender:  $BLENDER_VER"
echo ""
echo "   Next steps:"
echo "   1. Open Blender"
echo "   2. Edit → Preferences → Add-ons"
echo "   3. Search for 'AI Assistant'"
echo "   4. Enable it"
echo "   5. In 3D Viewport, open the Sidebar (N) → AI tab"
