"""
blender-mcp-ultra — Multi-Client Tests
Tests for MCP client compatibility.
"""
import sys
import os
import json
import subprocess
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Check if Blender MCP server is available
def is_blender_available():
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect(('localhost', 9876))
        sock.close()
        return True
    except:
        return False

skip_without_blender = pytest.mark.skipif(
    not is_blender_available(),
    reason="Blender MCP server not running"
)


class TestMCPProtocol:
    """Tests for MCP protocol compliance."""
    
    @skip_without_blender
    def test_initialize(self):
        """Test MCP initialize method."""
        result = subprocess.run(
            ['python3', '/home/carlosh/blender-mcp/mcp_adapter.py'],
            input=json.dumps({
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {}
            }),
            capture_output=True,
            text=True,
            timeout=10
        )
        response = json.loads(result.stdout)
        assert "result" in response
        assert "protocolVersion" in response["result"]
        assert "serverInfo" in response["result"]
    
    @skip_without_blender
    def test_tools_list(self):
        """Test MCP tools/list method."""
        result = subprocess.run(
            ['python3', '/home/carlosh/blender-mcp/mcp_adapter.py'],
            input=json.dumps({
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }),
            capture_output=True,
            text=True,
            timeout=10
        )
        response = json.loads(result.stdout)
        assert "result" in response
        assert "tools" in response["result"]
        assert len(response["result"]["tools"]) > 0
    
    @skip_without_blender
    def test_tools_call(self):
        """Test MCP tools/call method."""
        result = subprocess.run(
            ['python3', '/home/carlosh/blender-mcp/mcp_adapter.py'],
            input=json.dumps({
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "scene.get_info",
                    "arguments": {}
                }
            }),
            capture_output=True,
            text=True,
            timeout=10
        )
        response = json.loads(result.stdout)
        assert "result" in response
        assert "content" in response["result"]
    
    @skip_without_blender
    def test_ping(self):
        """Test MCP ping method."""
        result = subprocess.run(
            ['python3', '/home/carlosh/blender-mcp/mcp_adapter.py'],
            input=json.dumps({
                "jsonrpc": "2.0",
                "id": 4,
                "method": "ping",
                "params": {}
            }),
            capture_output=True,
            text=True,
            timeout=10
        )
        response = json.loads(result.stdout)
        assert "result" in response
        assert response["result"].get("pong") is True


class TestClientConfigs:
    """Tests for client configuration files."""
    
    def test_opencode_config_example_valid(self):
        """Contoh konfigurasi repo harus valid dan memuat server Blender."""
        repo_root = os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))))
        config_path = os.path.join(repo_root, "docs", "opencode.json.example")
        with open(config_path) as f:
            config = json.load(f)
        assert "mcp" in config
        assert any("blender" in name.lower() for name in config["mcp"])
    
    def test_docs_exist(self):
        """Dokumentasi client yang dikirim repo harus tersedia."""
        repo_root = os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))))
        docs_dir = os.path.join(repo_root, "docs")
        for filename in ("opencode.md", "claude-desktop.md", "cursor.md",
                         "vscode.md", "windsurf.md"):
            assert os.path.exists(os.path.join(docs_dir, filename))


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
