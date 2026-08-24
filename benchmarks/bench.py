#!/usr/bin/env python3
"""
Benchmarks de blender-mcp-ultra.
Mide: registro de tools, latencia socket round-trip, cache de tools, rst_search.
Uso: python benchmarks/bench.py [--json]
"""

import json
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

results = {}


def bench_registration():
    """Tiempo de crear el servidor MCP con 118 tools registradas."""
    from src.presentation.mcp_server import create_mcp_server

    times = []
    for _ in range(5):
        t0 = time.perf_counter()
        create_mcp_server()
        times.append((time.perf_counter() - t0) * 1000)
    results["registro_118_tools_ms"] = {
        "mediana": round(statistics.median(times), 1),
        "min": round(min(times), 1),
        "max": round(max(times), 1),
    }


def bench_socket(n=50):
    """Latencia round-trip ping por socket TCP al addon en Blender."""
    try:
        sys.path.insert(0, str(ROOT))
        from blender_connection import get_blender

        b = get_blender()
        b.send_command("ping")  # warmup
        lat = []
        for _ in range(n):
            t0 = time.perf_counter()
            b.send_command("ping")
            lat.append((time.perf_counter() - t0) * 1000)
        results["socket_ping_ms"] = {
            "n": n,
            "mediana": round(statistics.median(lat), 2),
            "p95": round(sorted(lat)[int(n * 0.95)], 2),
            "max": round(max(lat), 2),
        }
    except Exception as e:
        results["socket_ping_ms"] = {"error": f"Blender no disponible: {e}"}


def bench_execute_code():
    """Latencia de execute_code (bpy.app.timers round-trip)."""
    try:
        from blender_connection import get_blender

        b = get_blender()
        b.send_command("execute_code", {"code": "1+1"})
        lat = []
        for _ in range(10):
            t0 = time.perf_counter()
            b.send_command("execute_code", {"code": "len(bpy.data.objects)"})
            lat.append((time.perf_counter() - t0) * 1000)
        results["execute_code_ms"] = {
            "n": 10,
            "mediana": round(statistics.median(lat), 1),
            "max": round(max(lat), 1),
        }
    except Exception as e:
        results["execute_code_ms"] = {"error": str(e)}


def bench_cache():
    """Cache de resultados de tools: hit vs miss."""
    try:
        from src.tools import ToolRegistry
        from src.tools.scene import HANDLERS, TOOLS

        reg = ToolRegistry(use_cache=True)
        for t in TOOLS:
            if t.name in HANDLERS:
                reg.register_tool(t, HANDLERS[t.name])
        t0 = time.perf_counter()
        reg.execute_tool("scene.get_info", {})
        miss = (time.perf_counter() - t0) * 1000
        times_hit = []
        for _ in range(20):
            t0 = time.perf_counter()
            reg.execute_tool("scene.get_info", {})
            times_hit.append((time.perf_counter() - t0) * 1000)
        import statistics as st

        results["cache_tool_ms"] = {
            "miss": round(miss, 3),
            "hit_mediana": round(st.median(times_hit), 3),
        }
    except Exception as e:
        results["cache_tool_ms"] = {"error": str(e)}


def bench_rst_search():
    """Búsqueda en docs de la API (se ejecuta dentro de Blender; rst_search usa bpy)."""
    try:
        from blender_connection import get_blender

        b = get_blender()
        out = b.send_command(
            "execute_code",
            {
                "code": (
                    "import json, time\n"
                    "from addon.rst_search import search_api_docs\n"
                    "search_api_docs('cube')\n"
                    "lat=[]\n"
                    "for q in ['cube','light','camera','modifier','boolean']:\n"
                    "    t=time.perf_counter(); search_api_docs(q); lat.append((time.perf_counter()-t)*1000)\n"
                    "import statistics\n"
                    "print(json.dumps({'mediana': round(statistics.median(lat),2), 'max': round(max(lat),2)}))\n"
                )
            },
        )
        results["rst_search_ms"] = json.loads(out["output"].strip())
    except Exception as e:
        results["rst_search_ms"] = {"error": str(e)}


if __name__ == "__main__":
    print("Ejecutando benchmarks…\n")
    bench_registration()
    bench_socket()
    bench_execute_code()
    bench_cache()
    bench_rst_search()

    if "--json" in sys.argv:
        print(json.dumps(results, indent=2))
    else:
        for k, v in results.items():
            print(f"{k:24s} {v}")

    out = ROOT / "BENCHMARKS.md"
    lines = [
        "# BENCHMARKS.md — blender-mcp-ultra",
        "",
        f"Generado: {time.strftime('%Y-%m-%d %H:%M')} · Python {sys.version.split()[0]}",
        "",
        "| Métrica | Valor |",
        "|---|---|",
    ]
    for k, v in results.items():
        lines.append(f"| `{k}` | `{json.dumps(v)}` |")
    lines += [
        "",
        "Notas: socket/execute_code requieren Blender con el addon activo (:9876).",
        "",
    ]
    out.write_text("\n".join(lines))
    print(f"\nGuardado en {out}")
