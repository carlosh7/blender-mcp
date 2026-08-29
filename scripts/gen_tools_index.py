#!/usr/bin/env python3
"""Genera src/tools/context_search/data/tools_index.json desde el registry.

Se ejecuta en build (pre-empaquetado) para que tools.search funcione sin bpy.
"""

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from mcp_ultra.presentation.mcp_server import register_all_tools  # noqa: E402
from mcp_ultra.tools import ToolRegistry  # noqa: E402


def main() -> int:
    registry = ToolRegistry(use_cache=False)
    register_all_tools(registry)
    entries = []
    for tool in registry.list_tools():
        entries.append(
            {
                "name": tool.name,
                "category": tool.category.value
                if hasattr(tool.category, "value")
                else str(tool.category),
                "description": tool.description,
                "permission": tool.permission.value
                if hasattr(tool.permission, "value")
                else str(tool.permission),
                "parameters": tool.parameters or {},
            }
        )
    out = REPO / "mcp_ultra" / "tools" / "context_search" / "data" / "tools_index.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(entries, indent=1, ensure_ascii=False))
    print(f"OK: {out} ({len(entries)} tools)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
