#!/bin/bash
# blender-mcp — Environment Check (Linux)
echo ""
echo "================================================"
echo "  blender-mcp — System Check (Linux)"
echo "================================================"
echo ""

# Python
PY_V=$(python3 --version 2>/dev/null || python --version 2>/dev/null)
if [ $? -eq 0 ]; then
    echo -e "  \xE2\x9C\x85 Python: $PY_V"
else
    echo -e "  \xE2\x9D\x8C Python not found. Install: sudo apt install python3 python3-pip"
fi

# Blender
BL=$(which blender 2>/dev/null)
if [ -n "$BL" ]; then
    BL_V=$($BL --version 2>/dev/null | head -1)
    echo -e "  \xE2\x9C\x85 Blender: $BL_V"
    echo "         Path: $BL"
else
    echo -e "  \xE2\x9D\x8C Blender not found. Install: sudo apt install blender"
fi

# Disk space
FREE=$(df -h . | awk 'NR==2 {print $4}')
echo -e "  \xE2\x9C\x85 Disk free: $FREE"

# pip
if which pip3 >/dev/null 2>&1 || which pip >/dev/null 2>&1; then
    echo -e "  \xE2\x9C\x85 pip installed"
else
    echo -e "  \xE2\x9A\xA0\xEF\xB8\x8F pip not found. Install: sudo apt install python3-pip"
fi

echo ""
echo "================================================"
echo "  To install dependencies:"
echo "    pip3 install -r requirements.txt"
echo "================================================"
echo ""
