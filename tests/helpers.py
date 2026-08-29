"""
blender-mcp — Test Helpers
Shared utilities for test modules.
"""

import os
import socket
import sys
from pathlib import Path

import pytest


def socket_token():
    """Token del socket del addon: env BLENDER_TOKEN/BLENDER_MCP_TOKEN > archivo.

    El addon genera el token en <config>/blender-mcp/socket_token si no
    existe; los tests que hablan con el socket directamente deben enviarlo.
    """
    tok = os.getenv("BLENDER_TOKEN") or os.getenv("BLENDER_MCP_TOKEN") or ""
    if tok:
        return tok
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path.home() / ".config"
    try:
        return (base / "blender-mcp" / "socket_token").read_text(encoding="utf-8").strip()
    except Exception:
        return ""


def is_blender_available():
    """Check if Blender MCP server is running on port 9876."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect(("localhost", 9876))
        sock.close()
        return True
    except Exception:
        return False


_skip_blender_cache = None


def skip_without_blender(func=None, *, reason="Blender MCP server not running on port 9876"):
    """Decorator/marker to skip test when Blender is not available."""
    global _skip_blender_cache
    if _skip_blender_cache is None:
        _skip_blender_cache = not is_blender_available()

    marker = pytest.mark.skipif(_skip_blender_cache, reason=reason)
    if func is not None:
        return marker(func)
    return marker


class MCPSession:
    """Sesión JSON-RPC sobre stdio contra el gateway canónico (mcp_server.py)."""

    def __init__(self, server_cmd=None):
        import subprocess

        if server_cmd is None:
            repo_root = Path(__file__).resolve().parents[1]
            server_cmd = [sys.executable, str(repo_root / "mcp_server.py")]
        self.proc = subprocess.Popen(
            server_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        self._id = 0
        self.init_response = self.request(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "blender-mcp-tests", "version": "0"},
            },
        )
        self.notify("notifications/initialized")

    def request(self, method, params=None):
        self._id += 1
        req = {"jsonrpc": "2.0", "id": self._id, "method": method, "params": params or {}}
        self.proc.stdin.write(__import__("json").dumps(req) + "\n")
        self.proc.stdin.flush()
        while True:
            line = self.proc.stdout.readline()
            if not line:
                raise RuntimeError("el gateway cerró stdout")
            resp = __import__("json").loads(line)
            if resp.get("id") == self._id:
                return resp

    def notify(self, method, params=None):
        req = {"jsonrpc": "2.0", "method": method, "params": params or {}}
        self.proc.stdin.write(__import__("json").dumps(req) + "\n")
        self.proc.stdin.flush()

    def close(self):
        try:
            self.proc.stdin.close()
        except Exception:
            pass
        self.proc.terminate()
