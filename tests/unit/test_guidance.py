"""
blender-mcp-ultra — Guidance Tools Tests
guidance.list / guidance.get: contenido empaquetado en el wheel.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mcp_ultra.tools.guidance import get_guidance, list_guidance


class TestGuidanceList:
    def test_returns_topics(self):
        res = list_guidance()
        assert res["count"] >= 20
        assert len(res["topics"]) == res["count"]
        for entry in res["topics"]:
            assert entry["topic"] and entry["title"]

    def test_core_topics_present(self):
        topics = {t["topic"] for t in list_guidance()["topics"]}
        for expected in ("animation", "lighting", "materials", "modeling", "rendering", "workflow"):
            assert expected in topics

    def test_no_duplicates(self):
        topics = [t["topic"] for t in list_guidance()["topics"]]
        assert len(topics) == len(set(topics))


class TestGuidanceGet:
    def test_exact_topic(self):
        res = get_guidance("lighting")
        assert "error" not in res
        assert res["chars"] > 500
        assert res["content"].startswith("#")

    def test_normalization(self):
        # guion bajo, espacios y mayúsculas normalizan al mismo tema
        assert get_guidance("scene_setup")["topic"] == "scene-setup"
        assert get_guidance("Scene Setup")["topic"] == "scene-setup"

    def test_unknown_topic_lists_available(self):
        res = get_guidance("no-existe")
        assert "error" in res
        assert len(res["available"]) >= 20

    def test_missing_topic_requires_arg(self):
        res = get_guidance("")
        assert "error" in res
        assert "available" in res
