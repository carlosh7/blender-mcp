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

# ─── Chat Classes ───
class ChatMsg(PropertyGroup):
    role: StringProperty()
    text: StringProperty()
    is_new: BoolProperty(default=False)

class ChatData(PropertyGroup):
    msgs: CollectionProperty(type="ChatMsg")
    count: IntProperty(default=0)
    def add(self, r, t, is_update=False, scene=None):
        if is_update:
            while len(self.msgs) > 0 and self.msgs[-1].role == r and not self.msgs[-1].is_new:
                self.msgs.remove(len(self.msgs)-1)
            if len(self.msgs) > 0 and self.msgs[-1].role == r and self.msgs[-1].is_new:
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
class ModelItem(PropertyGroup):
    model_id: StringProperty(); model_name: StringProperty(); provider: StringProperty()

class ModelsData(PropertyGroup):
    items: CollectionProperty(type="ModelItem")
    count: IntProperty(default=0)
    def add(self, mid, name, prov):
        m = self.items.add(); m.model_id = mid; m.model_name = name; m.provider = prov; self.count = len(self.items)

def register_properties():
    """Register all shared properties onto bpy.types.Scene."""
    Scene = bpy.types.Scene

    # ⚡ Registro de Propiedades de Escena (Usando Strings para evitar fallos de orden)
    Scene.aimcp_chat = PointerProperty(type="ChatData")
    Scene.aimcp_models = PointerProperty(type="ModelsData")

    # ─── Integration Toggles (Fase 1) ───
    Scene.blendermcp_port = IntProperty(
        name="MCP Port", default=9876, min=1024, max=65535,
        description="Port for the Blender MCP socket server",
    )
    Scene.blendermcp_server_running = BoolProperty(default=False)

    # Poly Haven
    Scene.blendermcp_use_polyhaven = BoolProperty(
        name="Use Poly Haven", default=False,
        description="Enable Poly Haven HDRI/texture/model downloads",
    )

    # Sketchfab
    Scene.blendermcp_use_sketchfab = BoolProperty(
        name="Use Sketchfab", default=False,
        description="Enable Sketchfab model search and download",
    )
    Scene.blendermcp_sketchfab_api_key = StringProperty(
        name="Sketchfab API Key", default="", subtype='PASSWORD',
    )

    # Hyper3D Rodin
    Scene.blendermcp_use_hyper3d = BoolProperty(
        name="Use Hyper3D Rodin", default=False,
        description="Enable AI 3D model generation via Hyper3D Rodin",
    )
    Scene.blendermcp_hyper3d_mode = EnumProperty(
        name="Rodin Mode", default='MAIN_SITE',
        items=[
            ('MAIN_SITE', "Main Site", "Use hyper3d.ai (free trial or private key)"),
            ('FAL_AI', "FAL AI", "Use fal.ai (private key required)"),
        ],
    )
    Scene.blendermcp_hyper3d_api_key = StringProperty(
        name="Rodin API Key", default="", subtype='PASSWORD',
    )

    # Hunyuan3D
    Scene.blendermcp_use_hunyuan3d = BoolProperty(
        name="Use Hunyuan3D", default=False,
        description="Enable Tencent Hunyuan 3D model generation",
    )
    Scene.blendermcp_hunyuan3d_mode = EnumProperty(
        name="Hunyuan3D Mode", default='OFFICIAL_API',
        items=[
            ('OFFICIAL_API', "Official API", "Use Tencent Cloud API"),
            ('LOCAL_API', "Local API", "Use local Hunyuan3D API server"),
        ],
    )
    Scene.blendermcp_hunyuan3d_secret_id = StringProperty(
        name="SecretId", default="", subtype='PASSWORD',
    )
    Scene.blendermcp_hunyuan3d_secret_key = StringProperty(
        name="SecretKey", default="", subtype='PASSWORD',
    )
    Scene.blendermcp_hunyuan3d_api_url = StringProperty(
        name="API URL", default="http://localhost:8080",
    )
    Scene.blendermcp_hunyuan3d_octree_resolution = IntProperty(
        name="Octree Resolution", default=256, min=128, max=512,
    )
    Scene.blendermcp_hunyuan3d_num_inference_steps = IntProperty(
        name="Inference Steps", default=50, min=10, max=200,
    )
    Scene.blendermcp_hunyuan3d_guidance_scale = FloatProperty(
        name="Guidance Scale", default=5.0, min=1.0, max=20.0,
    )
    Scene.blendermcp_hunyuan3d_texture = BoolProperty(
        name="Generate Texture", default=True,
    )

    # AmbientCG
    Scene.blendermcp_use_ambientcg = BoolProperty(
        name="Use AmbientCG", default=False,
        description="Enable AmbientCG PBR material downloads",
    )

    # ─── Provider selector (Config panel) ───
    Scene.aimcp_provider = StringProperty(
        name="Provider", default="opencode-go",
        description="Current LLM provider ID",
    )

    # ─── Connection status (verificación al seleccionar modelo) ───
    Scene.aimcp_connection_status = StringProperty(
        name="Connection Status", default="",
        description="Estado de la conexión con el LLM (✅ conectado / 🔴 error)",
    )

    # ─── Agent Mode (Fase 4) ───
    Scene.blendermcp_agent_mode = EnumProperty(
        name="Agent Mode", default='AUTO',
        items=[
            ('AUTO', "Auto", "Use proxy if external MCP client connected, else autonomous"),
            ('PROXY', "Proxy", "Only use external MCP client (Claude/Cursor)"),
            ('AUTONOMOUS', "Autonomous", "Always use built-in agent (no external client needed)"),
        ],
        description="AI agent operation mode",
    )


def unregister_properties():
    """Clean up all registered properties."""
    attrs = [
        "blendermcp_port", "blendermcp_server_running",
        "blendermcp_use_polyhaven",
        "blendermcp_use_sketchfab", "blendermcp_sketchfab_api_key",
        "blendermcp_use_hyper3d", "blendermcp_hyper3d_mode", "blendermcp_hyper3d_api_key",
        "blendermcp_use_hunyuan3d", "blendermcp_hunyuan3d_mode",
        "blendermcp_hunyuan3d_secret_id", "blendermcp_hunyuan3d_secret_key",
        "blendermcp_hunyuan3d_api_url", "blendermcp_hunyuan3d_octree_resolution",
        "blendermcp_hunyuan3d_num_inference_steps", "blendermcp_hunyuan3d_guidance_scale",
        "blendermcp_hunyuan3d_texture",
        "blendermcp_use_ambientcg",
        "aimcp_provider",
        "blendermcp_agent_mode",
        "aimcp_connection_status",
    ]
    for a in attrs:
        if hasattr(bpy.types.Scene, a):
            try:
                delattr(bpy.types.Scene, a)
            except:
                pass
