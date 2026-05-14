"""
blender-mcp — Assembly Engine v2.0 MCP tools
"""
import json
from blender_connection import get_blender
from mcp.types import ToolAnnotations

def RW(**kw): return dict(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True), **kw)

def register_tools(mcp):
    @mcp.tool(**RW())
    def snap_to_anchor(obj_move: str, obj_target: str, anchor_move: str, anchor_target: str) -> str:
        """Une dos objetos haciendo coincidir sus anclas (27-pt system).
        Formatos de ancla: A_MIN_MIN_MIN, A_CENTER_CENTER_CENTER, A_MAX_MAX_MAX, etc."""
        b = get_blender()
        r = b.send_command("snap_to_anchor", {
            "obj_move": obj_move,
            "obj_target": obj_target,
            "anchor_move": anchor_move,
            "anchor_target": anchor_target
        })
        return json.dumps(r, indent=2)

    @mcp.tool(**RW())
    def snap_and_parent(obj_move: str, obj_target: str, anchor_move: str, anchor_target: str) -> str:
        """Snap determinista y vinculación jerárquica automática (Parenting). 
        Ideal para colgar focos en truss o poner equipos sobre tarimas."""
        b = get_blender()
        r = b.send_command("snap_and_parent", {
            "obj_move": obj_move,
            "obj_target": obj_target,
            "anchor_move": anchor_move,
            "anchor_target": anchor_target
        })
        return json.dumps(r, indent=2)

    @mcp.tool(**RW())
    def apply_symmetry(obj_name: str = "", axes_csv: str = "X,Y") -> str:
        """Aplica simetría industrial (Mirror) en los ejes indicados."""
        b = get_blender()
        axes = [a.strip() for a in axes_csv.split(",")]
        r = b.send_command("apply_symmetry", {"obj_name": obj_name, "axes": axes})
        return json.dumps(r, indent=2)
