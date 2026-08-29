"""
blender-mcp — Unified Creation Rules
Single source of truth: src/tools/objects/creation_rules.py

This module imports everything from mcp_ultra/tools/objects/creation_rules.py
addon/ files should import from this module instead of duplicating code.
"""

import sys
from pathlib import Path

# Add src to path for imports
_src_path = Path(__file__).parent.parent / "mcp_ultra"
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

# Import everything from source of truth
try:
    from tools.objects.creation_rules import *
    from tools.objects.creation_rules import (
        STANDARD_COLORS,
        STANDARD_OBJECTS,
        create_collection,
        create_object,
        get_collection_hierarchy,
        validate_connection,
        verify_connection,
    )

    _source = "mcp_ultra/tools/objects/creation_rules.py"
except ImportError as e:
    # Fallback: inline copy if src/ not available
    print(f"[creation_rules] Warning: Could not import from mcp_ultra/, using inline copy: {e}")
    _source = "inline"

    # This will be the fallback - copy the essential parts here
    # In production, this should never be needed
    raise ImportError(
        "src/tools/objects/creation_rules.py not found. "
        "Please ensure the src/ directory is available."
    )


def get_source():
    """Get the source of truth for this module."""
    return _source


__all__ = [
    "STANDARD_OBJECTS",
    "STANDARD_COLORS",
    "create_collection",
    "create_object",
    "get_collection_hierarchy",
    "validate_connection",
    "verify_connection",
    "get_source",
]
