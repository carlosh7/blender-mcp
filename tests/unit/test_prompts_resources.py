"""
Prompts & resources MCP del gateway — funcionan SIN Blender.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests"))

from helpers import MCPSession  # noqa: E402


class TestPrompts:
    def test_prompts_listed(self):
        s = MCPSession()
        try:
            resp = s.request("prompts/list")
        finally:
            s.close()
        names = [p["name"] for p in resp["result"]["prompts"]]
        assert {"product_shot", "archviz", "simple_scene"} <= set(names)

    def test_prompt_get(self):
        s = MCPSession()
        try:
            resp = s.request("prompts/get", {"name": "product_shot", "arguments": {}})
        finally:
            s.close()
        text = resp["result"]["messages"][0]["content"]["text"]
        assert "guidance.get" in text and "render.render" in text


class TestResources:
    def test_guidance_resource_template(self):
        s = MCPSession()
        try:
            resp = s.request("resources/read", {"uri": "blender://guidance/lighting"})
        finally:
            s.close()
        text = resp["result"]["contents"][0]["text"]
        assert "Light" in text or "light" in text
        assert len(text) > 300
