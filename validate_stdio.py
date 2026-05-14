#!/usr/bin/env python3
"""
validate_stdio.py — Valida el STDIO bridge.
Ejecuta el bridge y prueba comandos MCP básicos.
"""
import subprocess
import json
import sys
import os

BRIDGE = [sys.executable, os.path.join(os.path.dirname(__file__), "addon", "stdio_bridge.py")]

PASS = "✅"
FAIL = "❌"
tests = []

def test(name, input_data, check_fn):
    try:
        r = subprocess.run(BRIDGE, input=input_data,
                          capture_output=True, text=True, timeout=10)
        # Parse last JSON response
        lines = r.stdout.strip().split("\n")
        for line in reversed(lines):
            try:
                resp = json.loads(line)
                if check_fn(resp):
                    tests.append((name, PASS))
                    return
                else:
                    tests.append((name, f"{FAIL} respuesta inesperada"))
                    return
            except:
                continue
        tests.append((name, f"{FAIL} sin respuesta JSON valida"))
    except subprocess.TimeoutExpired:
        tests.append((name, f"{FAIL} timeout"))
    except Exception as e:
        tests.append((name, f"{FAIL} {e}"))

test("initialize", '{"method":"initialize","id":1}\n',
     lambda r: r.get("result", {}).get("protocolVersion") == "2024-11-05")

test("tools/list", '{"method":"tools/list","id":2}\n',
     lambda r: len(r.get("result", {}).get("tools", [])) > 10)

test("tools/call", '{"method":"tools/call","id":3,"params":{"name":"get_scene_info","arguments":{}}}\n',
     lambda r: "result" in r)

print(f"\n{'='*50}")
print(f"  VALIDACION STDIO BRIDGE")
print(f"{'='*50}")
passed = sum(1 for t in tests if PASS in t[1])
total = len(tests)
for n, s in tests:
    print(f"  {s} {n}")
print(f"{'='*50}")
print(f"  {passed}/{total} pruebas")
print(f"{'='*50}")
sys.exit(0 if passed == total else 1)
