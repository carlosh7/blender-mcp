#!/usr/bin/env python3
"""
stdio_bridge.py — Jembatan STDIO MCP untuk opencode dan klien STDIO.
Terhubung ke Blender via socket :9876. Tidak memerlukan SDK mcp.
Protokol: JSON-RPC lewat stdin/stdout (format MCP standar).

Katalog tools dan dispatch dibuat dari mcp_tools.py (satu sumber
kebenaran dengan mcp_server.py).
"""
import json
import os
import socket
import sys
import traceback

# Asegurar que el root del repo está en path para importar mcp_tools
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

HOST = "localhost"
PORT = 9876
BUFFER_SIZE = 65536

from mcp_tools import tool_schema, run_tool, TOOL_META  # noqa: E402


def call_blender(cmd_type, params=None):
    """Envía un comando a Blender vía socket y devuelve el resultado."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(180)
    try:
        s.connect((HOST, PORT))
        cmd = json.dumps({"command": cmd_type, "params": params or {}})
        s.sendall(cmd.encode())
        buffer = b""
        while True:
            chunk = s.recv(BUFFER_SIZE)
            if not chunk:
                break
            buffer += chunk
            try:
                data = json.loads(buffer.decode())
                return data.get("result", data)
            except json.JSONDecodeError:
                continue
        return {"error": "Tidak ada respons dari Blender"}
    except socket.timeout:
        return {"error": "Timeout saat terhubung ke Blender"}
    except ConnectionRefusedError:
        return {"error": "Blender tidak terbuka atau addon tidak aktif"}
    except Exception as e:
        return {"error": str(e)}
    finally:
        s.close()


TOOLS = tool_schema()


def handle_request(req):
    """Procesa una petición MCP y devuelve la respuesta."""
    method = req.get("method", "")
    req_id = req.get("id")

    if method == "initialize":
        return {"jsonrpc": "2.0", "id": req_id,
                "result": {"protocolVersion": "2024-11-05",
                           "capabilities": {"tools": {}},
                           "serverInfo": {"name": "blender-mcp",
                                          "version": "2.0.0",
                                          "tools": len(TOOLS)}}}

    elif method == "notifications/initialized":
        return None  # no response needed

    elif method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}}

    elif method == "tools/call":
        tool_name = req.get("params", {}).get("name", "")
        arguments = req.get("params", {}).get("arguments", {})
        if tool_name not in TOOL_META:
            return {"jsonrpc": "2.0", "id": req_id,
                    "error": {"code": -32601, "message": f"Tool tidak dikenal: {tool_name}"}}
        try:
            result = run_tool(tool_name, arguments)
        except Exception as e:
            result = {"error": f"{type(e).__name__}: {e}", "traceback": traceback.format_exc()}
        return {"jsonrpc": "2.0", "id": req_id,
                "result": {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}}

    elif method == "resources/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"resources": []}}

    return {"jsonrpc": "2.0", "id": req_id,
            "error": {"code": -32601, "message": f"Metode tidak dikenal: {method}"}}


def main():
    """STDIO MCP loop — lee JSON-RPC de stdin, escribe a stdout."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        response = handle_request(req)
        if response is None:
            continue
        sys.stdout.write(json.dumps(response) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
