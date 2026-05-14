#!/usr/bin/env python3
"""
stdio_bridge.py — STDIO MCP bridge para opencode y clientes STDIO.
Conecta a Blender vía socket :9876. No requiere el SDK mcp.
Protocolo: JSON-RPC sobre stdin/stdout (formato MCP estándar).
"""
import json
import socket
import sys
import traceback

HOST = "localhost"
PORT = 9876
BUFFER_SIZE = 65536


def call_blender(cmd_type, params=None):
    """Envía un comando a Blender vía socket y devuelve el resultado."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(180)
    try:
        s.connect((HOST, PORT))
        s.sendall(json.dumps({
            "command": cmd_type,
            "args": params or {},
        }).encode())

        buf = b""
        while True:
            chunk = s.recv(BUFFER_SIZE)
            if not chunk:
                break
            buf += chunk
            try:
                resp = json.loads(buf.decode())
                return resp.get("result", resp)
            except json.JSONDecodeError:
                continue
        return {"error": "Sin respuesta de Blender"}
    except socket.timeout:
        return {"error": "Timeout conectando con Blender"}
    except ConnectionRefusedError:
        return {"error": "Blender no está abierto o el addon no está activo"}
    except Exception as e:
        return {"error": str(e)}
    finally:
        s.close()


# ─── Definiciones de herramientas (mismas que en tools_*.py y handlers/) ───
TOOLS = [
    {"name": "get_scene_info", "description": "Get scene info (objects, counts)", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "get_object_info", "description": "Get object details", "inputSchema": {"type": "object", "properties": {"object_name": {"type": "string"}}, "required": ["object_name"]}},
    {"name": "execute_blender_code", "description": "Execute Python in Blender", "inputSchema": {"type": "object", "properties": {"code": {"type": "string"}}, "required": ["code"]}},
    {"name": "get_viewport_screenshot", "description": "Capture viewport", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "create_object", "description": "Create mesh object", "inputSchema": {"type": "object", "properties": {"type": {"type": "string", "enum": ["CUBE", "SPHERE", "CYLINDER", "CONE", "TORUS", "PLANE", "MONKEY"]}, "name": {"type": "string"}, "location": {"type": "array", "items": {"type": "number"}}}, "required": ["type"]}},
    {"name": "delete_object", "description": "Delete an object", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}},
    {"name": "transform_object", "description": "Move/rotate/scale object", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "location": {"type": "array", "items": {"type": "number"}}}, "required": ["name"]}},
    {"name": "create_material", "description": "Create PBR material", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "color": {"type": "array", "items": {"type": "number"}}, "roughness": {"type": "number"}, "metallic": {"type": "number"}}}},
    {"name": "assign_material", "description": "Assign material to object", "inputSchema": {"type": "object", "properties": {"object_name": {"type": "string"}, "material_name": {"type": "string"}}, "required": ["object_name", "material_name"]}},
    {"name": "create_light", "description": "Create light", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "light_type": {"type": "string", "enum": ["point", "sun", "spot", "area"]}, "energy": {"type": "number"}}}},
    {"name": "setup_three_point_lighting", "description": "Auto 3-point lighting", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "create_camera", "description": "Create camera", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "location": {"type": "array", "items": {"type": "number"}}, "lens": {"type": "number"}}}},
    {"name": "add_modifier", "description": "Add modifier to object", "inputSchema": {"type": "object", "properties": {"object_name": {"type": "string"}, "modifier_type": {"type": "string", "enum": ["subsurf", "bevel", "boolean", "array", "mirror", "solidify", "screw", "wireframe", "decimate", "triangulate"]}}, "required": ["modifier_type"]}},
    {"name": "export_scene", "description": "Export scene to file", "inputSchema": {"type": "object", "properties": {"filepath": {"type": "string"}, "format": {"type": "string", "enum": ["glb", "gltf", "fbx", "obj", "stl", "ply", "usd", "dae"]}}, "required": ["filepath", "format"]}},
    {"name": "unwrap_object", "description": "UV unwrap mesh", "inputSchema": {"type": "object", "properties": {"object_name": {"type": "string"}, "method": {"type": "string", "enum": ["smart", "unwrap", "cube", "cylinder", "sphere"]}}}},
    {"name": "render_frame", "description": "Render current frame", "inputSchema": {"type": "object", "properties": {"filepath": {"type": "string"}}}},
    {"name": "set_render_engine", "description": "Set render engine", "inputSchema": {"type": "object", "properties": {"engine": {"type": "string", "enum": ["CYCLES", "EEVEE", "WORKBENCH"]}}}},
    {"name": "check_manifold", "description": "Check if mesh is watertight", "inputSchema": {"type": "object", "properties": {"object_name": {"type": "string"}}}},
    {"name": "export_stl_mm", "description": "Export STL in mm for 3D printing", "inputSchema": {"type": "object", "properties": {"filepath": {"type": "string"}, "object_name": {"type": "string"}}, "required": ["filepath"]}},
    {"name": "search_polyhaven", "description": "Search Poly Haven assets", "inputSchema": {"type": "object", "properties": {"asset_type": {"type": "string", "enum": ["hdris", "textures", "models", "all"]}, "query": {"type": "string"}}}},
    {"name": "download_polyhaven_hdri", "description": "Download HDRI", "inputSchema": {"type": "object", "properties": {"asset_id": {"type": "string"}}, "required": ["asset_id"]}},
    {"name": "download_polyhaven_texture", "description": "Download PBR texture", "inputSchema": {"type": "object", "properties": {"asset_id": {"type": "string"}}, "required": ["asset_id"]}},
    {"name": "get_scene_visual", "description": "ASCII spatial visualization", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "mesh_analysis", "description": "Analyze mesh topology", "inputSchema": {"type": "object", "properties": {"object_name": {"type": "string"}}}},
    {"name": "purge_orphans", "description": "Remove unused data blocks", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "scene_summary", "description": "Full scene summary", "inputSchema": {"type": "object", "properties": {}}},
]


def handle_request(req):
    """Procesa una petición MCP y devuelve la respuesta."""
    method = req.get("method", "")
    req_id = req.get("id")

    if method == "initialize":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "serverInfo": {"name": "blender-mcp", "version": "0.8.27"}}}

    elif method == "notifications/initialized":
        return None  # no response needed

    elif method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}}

    elif method == "tools/call":
        tool_name = req.get("params", {}).get("name", "")
        arguments = req.get("params", {}).get("arguments", {})

        # Map tool name to command
        cmd_map = {
            "get_scene_info": ("get_scene_info", {}),
            "get_object_info": ("get_object_info", {"name": arguments.get("object_name", "")}),
            "execute_blender_code": ("execute_code", {"code": arguments.get("code", "")}),
            "get_viewport_screenshot": ("get_viewport_screenshot", {}),
            "create_object": ("create_object", {"type": arguments.get("type", "CUBE"), "name": arguments.get("name", ""), "location": arguments.get("location", (0, 0, 0))}),
            "delete_object": ("delete_object", {"name": arguments.get("name", "")}),
            "transform_object": ("transform_object", {"name": arguments.get("name", ""), "location": arguments.get("location")}),
            "create_material": ("create_material", arguments),
            "assign_material": ("assign_material", arguments),
            "create_light": ("create_light", arguments),
            "setup_three_point_lighting": ("setup_three_point_lighting", {}),
            "create_camera": ("create_camera", arguments),
            "add_modifier": ("add_modifier", arguments),
            "export_scene": ("export_scene", arguments),
            "unwrap_object": ("unwrap_object", arguments),
            "render_frame": ("render_frame", arguments),
            "set_render_engine": ("set_render_engine", arguments),
            "check_manifold": ("check_manifold", arguments),
            "export_stl_mm": ("export_stl_mm", arguments),
            "search_polyhaven": ("search_polyhaven", arguments),
            "download_polyhaven_hdri": ("download_polyhaven_hdri", arguments),
            "download_polyhaven_texture": ("download_polyhaven_texture", arguments),
            "get_scene_visual": ("get_scene_visual", {}),
            "mesh_analysis": ("mesh_analysis", arguments),
            "purge_orphans": ("purge_orphans", {}),
            "scene_summary": ("scene_summary", {}),
        }

        cmd_info = cmd_map.get(tool_name)
        if not cmd_info:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}}

        cmd_type, cmd_params = cmd_info
        result = call_blender(cmd_type, cmd_params)
        return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}}

    elif method == "resources/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"resources": []}}

    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Unknown method: {method}"}}


def main():
    """STDIO MCP loop — lee JSON-RPC de stdin, escribe a stdout."""
    buf = ""
    for line in sys.stdin:
        if not line:
            continue
        if line.startswith("Content-Length:"):
            continue
        buf += line
        try:
            req = json.loads(buf)
            buf = ""
        except json.JSONDecodeError:
            continue

        resp = handle_request(req)
        if resp is None:
            continue

        sys.stdout.write(json.dumps(resp) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
