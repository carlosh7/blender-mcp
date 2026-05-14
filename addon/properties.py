"""
blender-mcp — Scene Properties
All shared bpy.types.Scene properties for integrations and UI state.
"""
import bpy
from bpy.props import (
    BoolProperty, StringProperty, IntProperty, FloatProperty,
    EnumProperty, PointerProperty, CollectionProperty,
)
from bpy.types import PropertyGroup, UIList
from .chat_types import ChatMsg, ModelItem

# ─── Chat Classes ───

class ChatData(PropertyGroup):
    msgs: CollectionProperty(type=ChatMsg)
    count: IntProperty(default=0)
    def add(self, r, t, is_update=False, scene=None):
        if is_update:
            while len(self.msgs) > 0 and self.msgs[-1].role == r and not self.msgs[-1].is_new:
                self.msgs.remove(len(self.msgs)-1)
        m = self.msgs.add()
        m.role = r; m.text = t; m.is_new = True
        self.count = len(self.msgs)

class MCP_UL_Chat(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if not item: return
        row = layout.row(align=True)
        tag = "U" if item.role == "user" else "AI"
        row.label(text=f"[{tag}] {item.text}")

# ─── Model Classes ───

class ModelsData(PropertyGroup):
    items: CollectionProperty(type=ModelItem)
    count: IntProperty(default=0)
    
    def add(self, mid, name, prov):
        m = self.items.add()
        m.model_id = mid
        m.model_name = name
        m.provider = prov
        self.count = len(self.items)
        
    def clear_all(self):
        self.items.clear()
        self.count = 0

def register_properties():
    """Register all shared properties onto bpy.types.Scene."""
    Scene = bpy.types.Scene

    # 1. DATA CONTAINERS
    Scene.aimcp_chat = PointerProperty(type=ChatData)
    Scene.aimcp_models = PointerProperty(type=ModelsData)

    # 2. CHAT UI STATE
    Scene.aimcp_input = StringProperty(name="Input", default="")
    Scene.aimcp_connected = BoolProperty(name="Connected", default=False)
    Scene.aimcp_ai_state = StringProperty(default="disconnected")
    Scene.aimcp_status = StringProperty(name="Status", default="Ready")
    Scene.aimcp_waiting = BoolProperty(default=False)
    Scene.aimcp_spinner_idx = IntProperty(default=0)
    Scene.aimcp_connection_status = StringProperty(default="")
    Scene.aimcp_chat_index = IntProperty(default=0)
    Scene.aimcp_model = StringProperty(name="Selected Model", default="")

    # 3. INTEGRATION TOGGLES
    Scene.blendermcp_port = IntProperty(name="MCP Port", default=9876)
    Scene.blendermcp_server_running = BoolProperty(default=False)
    Scene.blendermcp_use_polyhaven = BoolProperty(name="Use Poly Haven", default=True)
    Scene.blendermcp_use_sketchfab = BoolProperty(name="Use Sketchfab", default=False)
    Scene.blendermcp_sketchfab_api_key = StringProperty(name="Sketchfab API Key", subtype='PASSWORD')
    Scene.blendermcp_use_hyper3d = BoolProperty(name="Use Hyper3D Rodin", default=False)
    Scene.blendermcp_hyper3d_api_key = StringProperty(name="Rodin API Key", subtype='PASSWORD')
    Scene.blendermcp_use_hunyuan3d = BoolProperty(name="Use Hunyuan3D", default=False)
    Scene.blendermcp_use_ambientcg = BoolProperty(name="Use AmbientCG", default=True)
    Scene.blendermcp_agent_mode = EnumProperty(
        name="Agent Mode", default='AUTO',
        items=[('AUTO', "Auto", ""), ('PROXY', "Proxy", ""), ('AUTONOMOUS', "Autonomous", "")]
    )
    Scene.aimcp_provider = StringProperty(name="Provider", default="opencode-go")

def unregister_properties():
    Scene = bpy.types.Scene
    props = [
        "aimcp_chat", "aimcp_models", "aimcp_input", "aimcp_connected", 
        "aimcp_ai_state", "aimcp_status", "aimcp_waiting", "aimcp_spinner_idx",
        "aimcp_connection_status", "aimcp_chat_index", "aimcp_model",
        "blendermcp_port", "blendermcp_server_running", "blendermcp_use_polyhaven",
        "blendermcp_use_sketchfab", "blendermcp_sketchfab_api_key",
        "blendermcp_use_hyper3d", "blendermcp_hyper3d_api_key",
        "blendermcp_use_hunyuan3d", "blendermcp_use_ambientcg",
        "blendermcp_agent_mode", "aimcp_provider"
    ]
    for p in props:
        if hasattr(Scene, p): delattr(Scene, p)
