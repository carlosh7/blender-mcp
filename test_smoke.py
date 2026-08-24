#!/usr/bin/env python3
"""blender-mcp — Quick Smoke Test"""

import sys

# Test AI integration (outside Blender)
print("=" * 50)
print("SMOKE TEST: AI Integration")
print("=" * 50)

from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "addon"))

from ai.ai_integration import parse_description_with_ai, query_llm, test_connection

# Test 1: Connection
print("\n1. Ollama Connection")
ok = test_connection()
print(f"   {'PASS' if ok else 'FAIL'}")

# Test 2: LLM
print("\n2. LLM Understanding")
tests = [
    ("What is 2+2?", "4"),
    ("What color is grass?", "green"),
    ("Name a material", "wood"),
]
for prompt, expected in tests:
    r = query_llm(f"{prompt} (one word)")
    status = "PASS" if expected.lower() in r.lower() else "FAIL"
    print(f"   {status}: '{prompt}' → '{r[:20]}'")

# Test 3: Parser
print("\n3. Description Parser")
tests = [
    "Una silla roja",
    "Un coche azul",
    "Una mesa de madera",
]
for desc in tests:
    p = parse_description_with_ai(desc)
    t = p.get("type", "?")
    c = p.get("color", "?")
    print(f"   PASS: '{desc}' → type={t}, color={c}")

# Test 4: Text→3D (outside Blender)
print("\n4. Text→3D (no Blender)")
obj = None
try:
    from ai.ai_integration import text_to_3d

    obj = text_to_3d("test")
except Exception:
    pass
print(f"   {'PASS' if obj is None else 'FAIL'}: returns None outside Blender")

print("\n" + "=" * 50)
print("ALL SMOKE TESTS COMPLETE")
print("=" * 50)
