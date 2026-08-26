"""
blender-mcp-ultra — Multi-Client Tests
Tests for MCP client compatibility.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from helpers import skip_without_blender

REPO_ROOT = Path(__file__).resolve().parents[2]
MCP_ADAPTER = str(REPO_ROOT / "mcp_adapter.py")


class TestMCPProtocol:
    """Tests for MCP protocol compliance."""

    @skip_without_blender
    def test_initialize(self):
        """Test MCP initialize method."""
        result = subprocess.run(
            ["python3", MCP_ADAPTER],
            input=json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}),
            capture_output=True,
            text=True,
            timeout=10,
        )
        response = json.loads(result.stdout)
        assert "result" in response
        assert "protocolVersion" in response["result"]
        assert "serverInfo" in response["result"]

    @skip_without_blender
    def test_tools_list(self):
        """Test MCP tools/list method."""
        result = subprocess.run(
            ["python3", MCP_ADAPTER],
            input=json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}),
            capture_output=True,
            text=True,
            timeout=10,
        )
        response = json.loads(result.stdout)
        assert "result" in response
        assert "tools" in response["result"]
        assert len(response["result"]["tools"]) > 0

    @skip_without_blender
    def test_tools_call(self):
        """Test MCP tools/call method."""
        result = subprocess.run(
            ["python3", MCP_ADAPTER],
            input=json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {"name": "scene.get_info", "arguments": {}},
                }
            ),
            capture_output=True,
            text=True,
            timeout=10,
        )
        response = json.loads(result.stdout)
        assert "result" in response
        assert "content" in response["result"]

    @skip_without_blender
    def test_ping(self):
        """Test MCP ping method."""
        result = subprocess.run(
            ["python3", MCP_ADAPTER],
            input=json.dumps({"jsonrpc": "2.0", "id": 4, "method": "ping", "params": {}}),
            capture_output=True,
            text=True,
            timeout=10,
        )
        response = json.loads(result.stdout)
        assert "result" in response
        assert response["result"].get("pong") is True


class TestClientConfigs:
    """Tests for client configuration files."""

    def test_opencode_config_exists(self):
        """Test opencode config file exists (skip: depende de la máquina local)."""
        config_path = os.path.expanduser("~/.config/opencode/opencode.json")
        if not os.path.exists(config_path):
            pytest.skip("opencode.json no instalado en esta máquina (test de entorno local)")
        assert os.path.exists(config_path)

    def test_opencode_config_valid(self):
        """Test opencode config is valid JSON (skip: depende de la máquina local)."""
        config_path = os.path.expanduser("~/.config/opencode/opencode.json")
        if not os.path.exists(config_path):
            pytest.skip("opencode.json no instalado en esta máquina (test de entorno local)")
        with open(config_path) as f:
            config = json.load(f)
        assert "mcp" in config
        assert "blender-mcp-ultra" in config["mcp"]

    def test_docs_exist(self):
        """Test client documentation files exist."""
        docs_dir = str(REPO_ROOT / "docs" / "clients")
        assert os.path.exists(docs_dir)
        assert os.path.exists(os.path.join(docs_dir, "opencode.md"))
        assert os.path.exists(os.path.join(docs_dir, "claude_desktop.md"))
        assert os.path.exists(os.path.join(docs_dir, "cursor.md"))
        assert os.path.exists(os.path.join(docs_dir, "vscode.md"))
        assert os.path.exists(os.path.join(docs_dir, "windsurf.md"))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
