#!/usr/bin/env python3
"""
blender-mcp — MCP Server for Blender 3D Model Generation.
Protocol: MCP (Model Context Protocol) via stdio.
Modes: standalone | check | gui

Usage:
  python server.py --mode standalone
  python server.py --mode check --check-path ../check-3d-planner/public/models
  python server.py --mode gui
"""

import json
import os
import sys
import shutil
import subprocess
import tempfile
import argparse
import textwrap
import time
import uuid
from pathlib import Path

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# ─── Paths ───
ROOT = Path(__file__).parent.resolve()
GENERATORS_DIR = ROOT / "generators"
MODELS_DIR = ROOT / "models"
os.makedirs(MODELS_DIR, exist_ok=True)

# ─── Blender detection ───
def find_blender():
    blender = shutil.which("blender.exe") or shutil.which("blender")
    if blender:
        return blender
    for p in ["/usr/bin/blender", "/snap/bin/blender"]:
        if os.path.isfile(p):
            return p
    return None

BLENDER_PATH = find_blender()

# ─── MCP Server ───
server = Server("blender-mcp")

# Current session state for iterative editing
session = {
    "mode": "standalone",
    "check_path": None,
    "last_script": None,
    "last_type": None,
    "last_params": None,
    "chat_queue": [],
    "chat_responses": {},
}


def run_blender(script_code: str, use_gui: bool = False) -> str:
    """Execute a Python script in Blender headless or GUI mode."""
    if not BLENDER_PATH:
        return "ERROR: Blender not found. Run check.py first."

    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
        f.write(script_code)
        script_path = f.name

    cmd = [BLENDER_PATH]
    if not use_gui:
        cmd.append("-b")
    cmd += ["--python-use-system-env", "--python", script_path]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        output = result.stdout + "\n" + result.stderr
        return output
    except subprocess.TimeoutExpired:
        return "ERROR: Blender timed out (120s)"
    finally:
        os.unlink(script_path)


def export_model(file_name: str) -> str:
    """Copy generated model to the correct output path."""
    src = MODELS_DIR / f"{file_name}.glb"
    if not src.exists():
        return "ERROR: Model file not found after generation"

    # If in check mode, copy to check-3d-planner
    if session["mode"] == "check" and session["check_path"]:
        dst = Path(session["check_path"]) / f"{file_name}.glb"
        shutil.copy2(src, dst)
        return str(dst)

    return str(src)


# ─── Tool: generate-model ───
AVAILABLE_MODELS = {
    "chair-folding": {"category": "seating", "width": 0.5, "depth": 0.5, "height": 0.9},
    "chair-executive": {"category": "seating", "width": 0.6, "depth": 0.6, "height": 0.9},
    "table-round-90": {"category": "tables", "width": 0.9, "depth": 0.9, "height": 0.75},
    "table-round-150": {"category": "tables", "width": 1.5, "depth": 1.5, "height": 0.75},
    "table-round-180": {"category": "tables", "width": 1.8, "depth": 1.8, "height": 0.75},
    "table-rect": {"category": "tables", "width": 1.8, "depth": 0.8, "height": 0.75},
    "platform-1x1": {"category": "stages", "width": 1.0, "depth": 1.0, "height": 0.2},
    "platform-2x2": {"category": "stages", "width": 2.0, "depth": 2.0, "height": 0.2},
    "stage-custom": {"category": "stages", "width": 6.0, "depth": 4.0, "height": 0.4},
    "runway": {"category": "stages", "width": 1.2, "depth": 4.0, "height": 0.2},
    "led-flat": {"category": "screens", "width": 1.6, "depth": 0.1, "height": 0.9},
    "speaker": {"category": "audio", "width": 0.4, "depth": 0.4, "height": 0.6},
    "truss-straight": {"category": "structure", "width": 2.0, "depth": 0.3, "height": 0.3},
    "barrier": {"category": "structure", "width": 2.0, "depth": 0.1, "height": 1.0},
}
MODEL_NAMES = sorted(AVAILABLE_MODELS.keys())
MODEL_HELP = "\n".join(f"  - {k}: {v['category']} ({v['width']}x{v['depth']}x{v['height']}m)" for k, v in AVAILABLE_MODELS.items())


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="generate-model",
            description="Generate a 3D model (GLTF/GLB) using Blender. Also supports iterative editing: regenerate with new params.",
            inputSchema={
                "type": "object",
                "properties": {
                    "model_type": {
                        "type": "string",
                        "description": f"Type of model to generate. Available types:\n{MODEL_HELP}",
                        "enum": MODEL_NAMES,
                    },
                    "name": {
                        "type": "string",
                        "description": "Output filename (without extension). Default: model_type value.",
                    },
                    "color": {
                        "type": "string",
                        "description": "Override base color in hex (e.g. '#ff0000') or 'random'. Default: type-specific.",
                    },
                    "material": {
                        "type": "string",
                        "description": "Material style: 'wood', 'metal', 'plastic', 'fabric'. Default: type-specific.",
                        "enum": ["wood", "metal", "plastic", "fabric", ""],
                    },
                    "scale": {
                        "type": "number",
                        "description": "Uniform scale multiplier (0.1 to 10). Default: 1.0.",
                    },
                    "gui": {
                        "type": "boolean",
                        "description": "Open Blender with GUI so you can see the result in real-time. Default: false.",
                    },
                    "iterative": {
                        "type": "boolean",
                        "description": "Keep Blender open and modify the existing scene (for iterative edits). Default: false.",
                    },
                },
                "required": ["model_type"],
            },
        ),
        types.Tool(
            name="list-models",
            description=f"List all available model types ({len(MODEL_NAMES)} total). Returns JSON with dimensions and categories.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="system-info",
            description="Get system info: OS, Python, Blender version, disk space.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="read-chat",
            description="Read pending chat messages from the Blender addon user. Returns a list of messages waiting for AI response.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="respond-chat",
            description="Respond to a pending chat message from Blender. The response will be sent back to the Blender addon chat panel.",
            inputSchema={
                "type": "object",
                "properties": {
                    "message_id": {
                        "type": "string",
                        "description": "ID of the message to respond to (from read-chat).",
                    },
                    "response": {
                        "type": "string",
                        "description": "The response text to send back to Blender. Can include model generation results or any AI response.",
                    },
                },
                "required": ["message_id", "response"],
            },
        ),
    ]


def generate_blender_script(model_type: str, name: str = None, color: str = None,
                             material: str = None, scale: float = 1.0,
                             iterative: bool = False) -> tuple[str, str]:
    """Generate a Blender Python script for the given model type.
    Returns (script_code, output_path).
    """
    out_name = name or model_type
    output_path = os.path.join(str(MODELS_DIR), f"{out_name}.glb")
    color_override = color or ""
    mat_override = material or ""

    # Color mapping
    color_map = {
        "chair-folding": (0.58, 0.64, 0.72, 0.12, 0.16, 0.20),
        "chair-executive": (0.12, 0.16, 0.20, 0.39, 0.45, 0.48),
        "table-round-90": (0.70, 0.33, 0.04, 0.47, 0.44, 0.42),
        "table-round-150": (0.70, 0.33, 0.04, 0.47, 0.44, 0.42),
        "table-round-180": (0.70, 0.33, 0.04, 0.47, 0.44, 0.42),
        "table-rect": (0.70, 0.33, 0.04, 0.47, 0.44, 0.42),
        "platform-1x1": (0.11, 0.24, 0.47, 0.23, 0.51, 0.96),
        "platform-2x2": (0.11, 0.24, 0.47, 0.23, 0.51, 0.96),
        "stage-custom": (0.11, 0.24, 0.47, 0.23, 0.51, 0.96),
        "runway": (0.11, 0.24, 0.47, 0.23, 0.51, 0.96),
        "led-flat": (0.06, 0.09, 0.16, 0.12, 0.25, 0.69),
        "speaker": (0.12, 0.16, 0.20, 0.20, 0.25, 0.33),
        "truss-straight": (0.80, 0.82, 0.87, 0.80, 0.82, 0.87),
        "barrier": (0.86, 0.15, 0.15, 0.97, 0.98, 1.00),
    }

    c = color_map.get(model_type, (0.5, 0.5, 0.5, 0.3, 0.3, 0.3))
    p1, p2, p3, s1, s2, s3 = c

    if color:
        # Parse hex color "#ff0000"
        hex_color = color.lstrip("#")
        if len(hex_color) == 6:
            r, g, b = int(hex_color[0:2], 16) / 255, int(hex_color[2:4], 16) / 255, int(hex_color[4:6], 16) / 255
            p1, p2, p3 = r, g, b
            s1, s2, s3 = r * 0.8, g * 0.8, b * 0.8

    clear_cmd = "bpy.ops.object.select_all(action='SELECT')\nbpy.ops.object.delete(use_global=False)"
    keep_cmd = "# Keep existing scene (iterative mode)"

    script = textwrap.dedent(f'''\
import bpy, os, math

# ─── Clean or keep scene ───
{keep_cmd if iterative else clear_cmd}

def make_mat(name, r, g, b, roughness=0.5, metalness=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes['Principled BSDF']
    bsdf.inputs['Base Color'].default_value = (r, g, b, 1)
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metalness
    return mat

S = {scale}
''')

    # Category-specific model generation
    cat = AVAILABLE_MODELS.get(model_type, {}).get("category", "")
    gen_script = ""

    if model_type == "chair-folding":
        gen_script = f'''
metal = make_mat('metal', {p1}, {p2}, {p3}, 0.3, 0.8)
plastic = make_mat('plastic', {s1}, {s2}, {s3}, 0.6, 0.0)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.44*S))
bpy.context.active_object.scale = (0.2*S, 0.2*S, 0.02*S)
bpy.context.active_object.data.materials.append(plastic)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.68*S))
bpy.context.active_object.scale = (0.2*S, 0.15*S, 0.02*S)
bpy.context.active_object.data.materials.append(plastic)
for x, z in [(-0.085*S, -0.085*S), (0.085*S, -0.085*S), (-0.085*S, 0.085*S), (0.085*S, 0.085*S)]:
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.01*S, depth=0.44*S, location=(x, 0, 0.22*S))
    bpy.context.active_object.data.materials.append(metal)
'''
    elif model_type.startswith("table-round"):
        diam = 0.9
        if "150" in model_type: diam = 1.5
        if "180" in model_type: diam = 1.8
        r = diam / 2 * scale
        gen_script = f'''
wood = make_mat('wood', {p1}, {p2}, {p3}, 0.6, 0.0)
metal = make_mat('metal', {s1}, {s2}, {s3}, 0.3, 0.8)
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius={r}, depth=0.04*S, location=(0, 0, 0.74*S))
bpy.context.active_object.data.materials.append(wood)
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius={r*0.6}, depth=0.04*S, location=(0, 0, 0.02*S))
bpy.context.active_object.data.materials.append(metal)
bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.02*S, depth=0.7*S, location=(0, 0, 0.38*S))
bpy.context.active_object.data.materials.append(metal)
'''
    elif model_type == "table-rect":
        gen_script = f'''
wood = make_mat('wood', {p1}, {p2}, {p3}, 0.6, 0.0)
metal = make_mat('metal', {s1}, {s2}, {s3}, 0.3, 0.8)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.74*S))
bpy.context.active_object.scale = (0.8*S, 0.35*S, 0.02*S)
bpy.context.active_object.data.materials.append(wood)
for x, z in [(-0.7*S, -0.3*S), (0.7*S, -0.3*S), (-0.7*S, 0.3*S), (0.7*S, 0.3*S)]:
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.02*S, depth=0.72*S, location=(x, 0, 0.38*S))
    bpy.context.active_object.data.materials.append(metal)
'''
    elif model_type in ("platform-1x1", "platform-2x2", "stage-custom", "runway"):
        w, d, h = 0.9, 0.9, 0.18
        if model_type == "platform-2x2": w, d, h = 1.9, 1.9, 0.18
        if model_type == "stage-custom": w, d, h = 5.8, 3.8, 0.35
        if model_type == "runway": w, d, h = 1.0, 3.8, 0.18
        gen_script = f'''
mat = make_mat('stage', {p1}, {p2}, {p3}, 0.5, 0.0)
edge = make_mat('edge', {s1}, {s2}, {s3}, 0.3, 0.0)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, {h/2}*S))
bpy.context.active_object.scale = ({w/2}*S, {d/2}*S, {h/2}*S)
bpy.context.active_object.data.materials.append(mat)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, {h}*S))
bpy.context.active_object.scale = ({w/2}*S, {d/2}*S, 0.003*S)
bpy.context.active_object.data.materials.append(edge)
'''
    elif model_type == "led-flat":
        gen_script = f'''
body = make_mat('body', {p1}, {p2}, {p3}, 0.3, 0.0)
face = make_mat('face', {s1}, {s2}, {s3}, 0.2, 0.0)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.45*S))
bpy.context.active_object.scale = (0.7*S, 0.04*S, 0.4*S)
bpy.context.active_object.data.materials.append(body)
bpy.ops.mesh.primitive_cylinder_add(vertices=4, radius=0.015*S, depth=0.3*S, location=(0, 0, 0.15*S))
bpy.context.active_object.data.materials.append(body)
'''
    elif model_type == "speaker":
        gen_script = f'''
body = make_mat('body', {p1}, {p2}, {p3}, 0.5, 0.0)
cone = make_mat('cone', {s1}, {s2}, {s3}, 0.6, 0.0)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.25*S))
bpy.context.active_object.scale = (0.175*S, 0.25*S, 0.175*S)
bpy.context.active_object.data.materials.append(body)
bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.06*S, depth=0.04*S, location=(0.18*S, 0, 0.35*S))
bpy.context.active_object.rotation_euler = (0, 1.5708, 0)
bpy.context.active_object.data.materials.append(cone)
'''
    elif model_type == "truss-straight":
        gen_script = f'''
mat = make_mat('truss', {p1}, {p2}, {p3}, 0.3, 0.6)
for x, z in [(-0.15*S, -0.15*S), (0.15*S, -0.15*S), (-0.15*S, 0.15*S), (0.15*S, 0.15*S)]:
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.015*S, depth=1.9*S, location=(x, 0, 0.95*S))
    bpy.context.active_object.data.materials.append(mat)
for i in range(6):
    y = i * 0.35 * S + 0.1*S
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, y))
    bpy.context.active_object.scale = (0.15*S, 0.006*S, 0.006*S)
    bpy.context.active_object.data.materials.append(mat)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, y))
    bpy.context.active_object.scale = (0.006*S, 0.15*S, 0.006*S)
    bpy.context.active_object.data.materials.append(mat)
'''
    elif model_type == "barrier":
        gen_script = f'''
red = make_mat('red', {p1}, {p2}, {p3}, 0.5, 0.0)
white = make_mat('white', {s1}, {s2}, {s3}, 0.5, 0.0)
for y, c in [(0.85*S, 'red'), (0.55*S, 'white'), (0.25*S, 'red')]:
    mat = red if c == 'red' else white
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, y))
    bpy.context.active_object.scale = (0.9*S, 0.02*S, 0.02*S)
    bpy.context.active_object.data.materials.append(mat)
for x in [-0.85*S, 0.85*S]:
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 0, 0.45*S))
    bpy.context.active_object.scale = (0.02*S, 0.02*S, 0.45*S)
    bpy.context.active_object.data.materials.append(white)
'''
    else:
        gen_script = f'''
mat = make_mat('default', {p1}, {p2}, {p3}, 0.5, 0.0)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.5*S))
bpy.context.active_object.scale = (0.5*S, 0.5*S, 0.5*S)
bpy.context.active_object.data.materials.append(mat)
'''

    script += gen_script

    # Export
    script += textwrap.dedent(f'''\

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
os.makedirs(os.path.dirname('{output_path}'), exist_ok=True)
bpy.ops.export_scene.gltf(filepath='{output_path}', export_format='GLB')
print(f"EXPORTED: {{os.path.getsize('{output_path}')}} bytes")
''')

    return script, output_path


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[types.TextContent]:
    if not arguments:
        arguments = {}

    if name == "list-models":
        return [types.TextContent(type="text", text=json.dumps(AVAILABLE_MODELS, indent=2))]

    if name == "system-info":
        from config import get_system_info
        info = get_system_info()
        return [types.TextContent(type="text", text=json.dumps(info, indent=2))]

    if name == "generate-model":
        model_type = arguments.get("model_type", "")
        if model_type not in AVAILABLE_MODELS:
            return [types.TextContent(type="text", text=f"Unknown model: {model_type}. Use list-models to see available types.")]

        # Parameters
        name = arguments.get("name", model_type)
        color = arguments.get("color")
        material = arguments.get("material", "")
        scale = float(arguments.get("scale", 1.0))
        use_gui = bool(arguments.get("gui", False)) or session.get("gui", False)
        iterative = bool(arguments.get("iterative", False))

        # Store for iterative editing
        session["last_type"] = model_type
        session["last_params"] = {"name": name, "color": color, "material": material, "scale": scale}

        # Generate and run
        script, output_path = generate_blender_script(
            model_type, name=name, color=color, material=material,
            scale=scale, iterative=iterative
        )
        session["last_script"] = script

        result = run_blender(script, use_gui=use_gui)

        if os.path.exists(output_path):
            size = os.path.getsize(output_path)
            # Copy to check path if needed
            final_path = output_path
            if session["mode"] == "check" and session["check_path"]:
                dst = Path(session["check_path"]) / f"{name}.glb"
                shutil.copy2(output_path, dst)
                final_path = str(dst)

            return [types.TextContent(type="text", text=json.dumps({
                "success": True,
                "file": final_path,
                "size_bytes": size,
                "size_kb": round(size / 1024, 1),
                "output_preview": result[:500],
            }, indent=2))]
        else:
            return [types.TextContent(type="text", text=f"FAILED to generate model. Blender output:\n{result[:2000]}")]

    if name == "read-chat":
        pending = []
        for msg in session["chat_queue"]:
            pending.append({
                "id": msg["id"],
                "message": msg["message"],
                "timestamp": msg["timestamp"],
            })
        return [types.TextContent(type="text", text=json.dumps({"messages": pending}, indent=2))]

    if name == "respond-chat":
        msg_id = arguments.get("message_id", "")
        response = arguments.get("response", "")
        if not msg_id or not response:
            return [types.TextContent(type="text", text="Error: message_id and response are required")]
        session["chat_responses"][msg_id] = response
        # Remove from queue
        session["chat_queue"] = [m for m in session["chat_queue"] if m["id"] != msg_id]
        return [types.TextContent(type="text", text=json.dumps({"success": True, "message_id": msg_id}))]

    return [types.TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    parser = argparse.ArgumentParser(description="blender-mcp: AI-powered 3D model generation via Blender")
    parser.add_argument("--mode", choices=["standalone", "check", "gui", "all"], default="standalone",
                        help="Operation mode. 'all' enables everything simultaneously.")
    parser.add_argument("--check-path", type=str, default=None,
                        help="Path to check-3d-planner's public/models directory")
    parser.add_argument("--gui", action="store_true", default=False,
                        help="Open Blender with GUI visible (even in standalone/check mode)")
    parser.add_argument("--ws-port", type=int, default=9876,
                        help="WebSocket port for Blender addon connection")
    args = parser.parse_args()

    # Resolve mode aliases
    if args.mode == "all":
        args.mode = "standalone"  # base mode
        args.gui = True
        args.check_path = args.check_path or str(MODELS_DIR.parent / "check-3d-planner" / "public" / "models")

    session["mode"] = args.mode
    session["gui"] = args.gui
    if args.check_path:
        session["check_path"] = os.path.abspath(args.check_path)
        os.makedirs(session["check_path"], exist_ok=True)

    from config import print_summary
    print_summary()

    # Start HTTP bridge for Blender addon
    try:
        from http_bridge import start_http_server
        start_http_server(args.ws_port + 11)  # 9876 + 11 = 9877
    except Exception as e:
        print(f"  HTTP Bridge: not started ({e})")

    print(f"  Mode:      {args.mode}")
    print(f"  Output:    {session['check_path'] or MODELS_DIR}")
    print(f"  Blender:   {BLENDER_PATH or 'NOT FOUND'}")
    print(f"  WS Port:   {args.ws_port} (for Blender addon)")
    print(f"\n  Ready. Connect via MCP stdio or WebSocket.\n")

    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, write_stream,
            InitializationOptions(
                server_name="blender-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
