#!/bin/bash
# install.sh — Install blender-mcp addon for Blender (Linux)
# Detects Blender version and copies addon files to the correct directory.

set -e

ADDON_SRC="$(dirname "$0")/addon"

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

if [ ! -d "$ADDON_SRC" ]; then
    echo "❌ Addon source not found: $ADDON_SRC"
    echo "   Run this script from the blender-mcp root directory."
    exit 1
fi

mkdir -p "$ADDON_DIR"
cp -r "$ADDON_SRC"/* "$ADDON_DIR/"
echo "✅ blender-mcp addon installed!"
echo "   Location: $ADDON_DIR"
echo "   Blender:  $BLENDER_VER"
echo ""
echo "   Next steps:"
echo "   1. Open Blender"
echo "   2. Edit → Preferences → Add-ons"
echo "   3. Search for 'AI Assistant'"
echo "   4. Enable it"
echo "   5. In 3D Viewport, press N → AI tab"
