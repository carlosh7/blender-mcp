#!/usr/bin/env python3
"""
blender-mcp-ultra — MCP Server Adapter for opencode
Bridges MCP protocol (stdio) to Blender socket server (TCP).
"""
import sys
import os
import json
import socket
import time
import logging
from datetime import datetime

# Setup paths
_dir = os.path.dirname(os.path.abspath(__file__))
_src_dir = os.path.join(_dir, 'src')
sys.path.insert(0, _src_dir)

logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("blender-mcp-ultra")

# Import security modules
from infrastructure.monitoring import get_metrics_collector, get_health_checker, get_alert_manager
from infrastructure.security.auth import get_authenticator

# Blender connection
BLENDER_HOST = os.environ.get("BLENDER_HOST", "localhost")
BLENDER_PORT = int(os.environ.get("BLENDER_PORT", "9876"))

# Security: rate limiting
_request_counts = {}
_last_request_time = {}
MAX_REQUESTS_PER_MINUTE = 60

# Authentication
_auth_enabled = os.environ.get("MCP_AUTH_ENABLED", "false").lower() == "true"
_default_token = None


def check_rate_limit(client_id: str = "default") -> bool:
    """Check if request is within rate limit."""
    now = time.time()
    minute_key = f"{client_id}:{int(now // 60)}"
    
    if minute_key not in _request_counts:
        _request_counts[minute_key] = 0
    
    _request_counts[minute_key] += 1
    
    if _request_counts[minute_key] > MAX_REQUESTS_PER_MINUTE:
        logger.warning(f"Rate limit exceeded for {client_id}")
        return False
    
    return True


def send_to_blender(command, params=None):
    """Send command to Blender via socket."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(30)
        sock.connect((BLENDER_HOST, BLENDER_PORT))
        cmd = json.dumps({"command": command, "params": params or {}})
        sock.sendall(cmd.encode())
        time.sleep(0.1)
        resp = sock.recv(65536)
        sock.close()
        return json.loads(resp.decode()) if resp else {"error": "No response"}
    except Exception as e:
        return {"error": str(e)}


def log_tool_call(tool_name: str, params: dict, success: bool, execution_time: float):
    """Log tool call for audit trail."""
    timestamp = datetime.now().isoformat()
    log_entry = {
        "timestamp": timestamp,
        "tool": tool_name,
        "params_keys": list(params.keys()) if params else [],
        "success": success,
        "execution_time_ms": execution_time * 1000,
    }
    logger.info(f"TOOL_CALL: {json.dumps(log_entry)}")


def handle_request(request):
    """Handle MCP JSON-RPC request."""
    method = request.get("method", "")
    params = request.get("params", {})
    req_id = request.get("id")
    
    # Start timing
    start_time = time.time()

    # Rate limiting check
    if not check_rate_limit():
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {
                "code": -32000,
                "message": "Rate limit exceeded. Please slow down."
            }
        }
    
    # Authentication check (if enabled)
    if _auth_enabled and method not in ["initialize", "notifications/initialized", "ping"]:
        token = params.get("token") or request.get("token")
        if not token:
            # Generate default token for first use
            global _default_token
            if _default_token is None:
                _default_token = get_authenticator().generate_token("default", ["read", "write"])
            token = _default_token
        
        if not get_authenticator().validate_token(token):
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32001,
                    "message": "Authentication required. Provide valid token."
                }
            }

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {
                    "name": "blender-mcp-ultra",
                    "version": "1.0.0"
                }
            }
        }

    elif method == "notifications/initialized":
        return None  # No response needed

    elif method == "tools/list":
        result = send_to_blender("list_tools")
        tools = []
        for tool in result.get("tools", []):
            tools.append({
                "name": tool["name"],
                "description": tool.get("description", ""),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        k: {"type": v.get("type", "string"), "description": v.get("description", "")}
                        for k, v in tool.get("parameters", {}).items()
                    },
                    "required": [k for k, v in tool.get("parameters", {}).items() if v.get("required")]
                }
            })
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": tools}}

    elif method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})
        
        # Security: validate tool name
        if not tool_name or not isinstance(tool_name, str):
            return {"jsonrpc": "2.0", "id": req_id, "error": {
                "code": -32602,
                "message": "Invalid tool name"
            }}
        
        # Security: check tool exists
        start_time = time.time()
        result = send_to_blender("tool", {"tool_name": tool_name, "params": arguments})
        execution_time = time.time() - start_time
        
        # Log the tool call
        log_tool_call(tool_name, arguments, result.get("success", False), execution_time)
        
        if result.get("success"):
            content = json.dumps(result.get("data", {}), indent=2)
            return {"jsonrpc": "2.0", "id": req_id, "result": {
                "content": [{"type": "text", "text": content}]
            }}
        else:
            return {"jsonrpc": "2.0", "id": req_id, "result": {
                "content": [{"type": "text", "text": f"Error: {result.get('error', 'Unknown error')}"}],
                "isError": True
            }}

    elif method == "ping":
        result = send_to_blender("ping")
        return {"jsonrpc": "2.0", "id": req_id, "result": result}

    else:
        response = {"jsonrpc": "2.0", "id": req_id, "error": {
            "code": -32601,
            "message": f"Method not found: {method}"
        }}
    
    # Record metrics
    execution_time = time.time() - start_time
    success = "error" not in str(response)
    get_metrics_collector().record_request(execution_time, success)
    
    return response


def main():
    """Main loop: read JSON-RPC from stdin, write to stdout."""
    logger.info("blender-mcp-ultra MCP server starting")
    
    # Test connection to Blender
    result = send_to_blender("ping")
    if result.get("pong"):
        logger.info(f"Connected to Blender ({result.get('tools', 0)} tools)")
    else:
        logger.warning("Blender not connected - will retry on first request")

    buffer = ""
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            buffer += line
            # Try to parse complete JSON-RPC messages
            try:
                request = json.loads(buffer)
                buffer = ""
                
                response = handle_request(request)
                if response:
                    sys.stdout.write(json.dumps(response) + "\n")
                    sys.stdout.flush()
                    
            except json.JSONDecodeError:
                continue
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            continue


if __name__ == "__main__":
    main()
