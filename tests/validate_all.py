#!/usr/bin/env python3
"""
validate_all.py — Ejecuta todas las validaciones y resume.
"""
import subprocess
import sys
import os

SCRIPTS = [
    ("🔌 Blender Socket", "validate_tools.py"),
    ("🔌 STDIO Bridge", "validate_stdio.py"),
    ("🌐 HTTP API", "validate_http.py"),
]

RESULTS = []

for name, script in SCRIPTS:
    path = os.path.join(os.path.dirname(__file__), script)
    print(f"\n▶  {name} ({script})")
    print(f"{'─'*50}")
    try:
        r = subprocess.run([sys.executable, path],
                          capture_output=True, text=True, timeout=120)
        # Show last 10 lines
        lines = (r.stdout or "").strip().split("\n")
        for line in lines[-8:]:
            print(f"  {line}")
        if r.returncode == 0:
            RESULTS.append((name, "✅"))
        else:
            RESULTS.append((name, "❌"))
    except subprocess.TimeoutExpired:
        print("  ⚠️  Timeout (120s)")
        RESULTS.append((name, "❌ timeout"))
    except FileNotFoundError:
        print(f"  ⚠️  Script no encontrado: {path}")
        RESULTS.append((name, "❌ no encontrado"))

print(f"\n{'='*50}")
print(f"  RESUMEN DE VALIDACION")
print(f"{'='*50}")
for name, status in RESULTS:
    print(f"  {status} {name}")
print(f"{'='*50}")
total_ok = sum(1 for _, s in RESULTS if s == "✅")
total = len(RESULTS)
print(f"  {total_ok}/{total} pruebas exitosas")
print(f"{'='*50}")
sys.exit(0 if total_ok == total else 1)
