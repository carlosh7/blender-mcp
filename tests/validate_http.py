#!/usr/bin/env python3
"""
validate_http.py — Valida el HTTP API de Antigravity.
Requiere Blender abierto con el addon activo.
"""
import urllib.request
import urllib.error
import json
import sys

BASE = "http://localhost:9877"
PASS = "✅"
FAIL = "❌"
tests = []

def test(name, url, check_fn, method="GET", body=None):
    try:
        if method == "GET":
            r = urllib.request.urlopen(url, timeout=5)
        else:
            req = urllib.request.Request(url, data=body,
                headers={"Content-Type": "application/json"})
            r = urllib.request.urlopen(req, timeout=5)
        data = json.loads(r.read())
        if check_fn(data):
            tests.append((name, PASS))
        else:
            tests.append((name, f"{FAIL} respuesta inesperada: {json.dumps(data)[:100]}"))
    except urllib.error.HTTPError as e:
        tests.append((name, f"{FAIL} HTTP {e.code}"))
    except urllib.error.URLError:
        tests.append((name, f"{FAIL} conexión rehusada (Blender cerrado?)"))
    except Exception as e:
        tests.append((name, f"{FAIL} {e}"))

test("health", f"{BASE}/api/health", lambda d: d.get("status") == "ok")
test("tools", f"{BASE}/api/tools", lambda d: d.get("count", 0) > 0)
test("chat POST", f"{BASE}/api/chat", lambda d: d.get("status") == "queued",
     method="POST", body=json.dumps({"message": "test"}).encode())

print(f"\n{'='*50}")
print(f"  VALIDACION HTTP API")
print(f"{'='*50}")
if any("conexión rehusada" in t[1] for t in tests):
    print(f"  ⚠️  Blender no está abierto con el addon activo")
    print(f"  Abre Blender y activa el addon primero")
    print(f"{'='*50}")
    sys.exit(1)
passed = sum(1 for t in tests if PASS in t[1])
total = len(tests)
for n, s in tests:
    print(f"  {s} {n}")
print(f"{'='*50}")
print(f"  {passed}/{total} pruebas")
print(f"{'='*50}")
sys.exit(0 if passed == total else 1)
