#!/usr/bin/env python3
"""Genera docs/TOOLS.md desde el registry vivo (fuente de verdad única).

Uso: python scripts/gen_tools_docs.py
El CI verifica que el fichero committeado esté en sync (`git diff --exit-code`).
"""

import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from mcp_ultra.presentation.mcp_server import register_all_tools  # noqa: E402
from mcp_ultra.tools import ToolRegistry  # noqa: E402

OUT = REPO / "docs" / "TOOLS.md"


def main() -> int:
    registry = ToolRegistry()
    register_all_tools(registry)
    tools = registry.list_tools()

    by_category: dict[str, list] = defaultdict(list)
    for tool in tools:
        by_category[tool.category.value].append(tool)

    lines = [
        "<!-- GENERADO: scripts/gen_tools_docs.py — no editar a mano -->",
        "",
        f"# Referencia de tools ({len(tools)})",
        "",
        f"Registry completo: {len(tools)} tools en {len(by_category)} categorías. "
        "Generado desde `mcp_ultra/tools/` (la misma fuente que usa el gateway).",
        "",
        "| Categoría | Tools |",
        "|---|---|",
    ]
    for cat in sorted(by_category):
        names = ", ".join(f"`{t.name}`" for t in sorted(by_category[cat], key=lambda t: t.name))
        lines.append(f"| `{cat}` | {names} |")

    lines += ["", "---", ""]
    for cat in sorted(by_category):
        lines += [f"## {cat}", ""]
        for tool in sorted(by_category[cat], key=lambda t: t.name):
            lines += [f"### `{tool.name}`", "", tool.description or "", ""]
            if tool.parameters:
                lines += ["| Parámetro | Tipo | Req | Default |", "|---|---|---|---|"]
                for pname, pdef in tool.parameters.items():
                    ptype = str(pdef.get("type", "str"))
                    req = "✅" if pdef.get("required") else ""
                    default = pdef.get("default", "")
                    default = f"`{default}`" if default != "" else ""
                    lines.append(f"| `{pname}` | {ptype} | {req} | {default} |")
                lines.append("")
            if tool.examples:
                lines += ["Ejemplos:"] + [f"- `{ex}`" for ex in tool.examples] + [""]
            lines += [""]

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"OK: {OUT} ({len(tools)} tools, {len(by_category)} categorías)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
