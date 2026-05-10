# blender-mcp — AI Assistant for Blender v0.5.0
# Panels: Config (Properties) + Chat (3D View Sidebar) + HTTP bridge
bl_info = {
    "name": "AI Assistant (blender-mcp)",
    "author": "carlosh7",
    "version": (0, 5, 0),
    "blender": (4, 0, 0),
    "location": "Properties > Scene > AI Config | View3D > Sidebar (N) > AI Chat",
    "description": "Chat with AI to create 3D models. Config panel in Properties, chat in 3D View sidebar.",
    "doc_url": "https://github.com/carlosh7/blender-mcp",
    "category": "3D View",
}
import bpy, os, json, urllib.request, urllib.error
from bpy.types import Panel, Operator, PropertyGroup, UIList
from bpy.props import StringProperty, IntProperty, BoolProperty, PointerProperty, CollectionProperty

HTTP_HOST = "http://localhost:9877"

# ─── Helpers ───
def http_get(path):
    try:
        r = urllib.request.urlopen(f"{HTTP_HOST}{path}", timeout=3)
        return json.loads(r.read())
    except: return None

def http_post(path, data):
    try:
        body = json.dumps(data).encode()
        req = urllib.request.Request(f"{HTTP_HOST}{path}", data=body,
            headers={"Content-Type": "application/json"}, method="POST")
        r = urllib.request.urlopen(req, timeout=30)
        return json.loads(r.read())
    except Exception as e:
        return {"error": str(e)}

# ─── Chat types ───
class ChatMsg(PropertyGroup):
    role: StringProperty(name="Role")
    text: StringProperty(name="Text")

class ChatData(PropertyGroup):
    msgs: CollectionProperty(type=ChatMsg)
    count: IntProperty(name="Count", default=0)
    def add(self, role, text):
        m = self.msgs.add(); m.role = role; m.text = text
        self.count = len(self.msgs)
    def clear_all(self):
        while self.msgs: self.msgs.remove(0)
        self.count = 0

# ─── Scrollable Chat List ───
class MCP_UL_Chat(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        tag = "You" if item.role == "user" else "AI" if item.role == "assistant" else "Sys"
        col = layout.column()
        col.scale_y = 1.5
        col.label(text=f"[{tag}]")
        for line in item.text.split("\n"):
            col.label(text=f"  {line[:120]}")

# ─── Properties Panel (Config) ───
class PN_PT_Config(Panel):
    bl_label = "AI Assistant Config"
    bl_idname = "PN_PT_Config"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'scene'

    def draw(self, ctx):
        L = self.layout
        c = ctx.scene

        # Connection
        box = L.box()
        box.label(text="Server Connection", icon='LINKED')
        row = box.row(align=True)
        row.prop(c, "aimcp_server_host", text="Host")
        row.prop(c, "aimcp_server_port", text="Port")

        row = box.row(align=True)
        connected = getattr(c, "aimcp_connected", False)
        if connected:
            row.label(text="Online", icon='CHECKBOX_HLT')
        else:
            row.label(text="Offline", icon='CHECKBOX_DEHLT')
        row.operator("aimcp.check_connection", text="Check")

        # Model selector (text input - type any model from opencode/openrouter)
        L.separator()
        box = L.box()
        box.label(text="AI Model (opencode)", icon='SETTINGS')
        row = box.row(align=True)
        row.prop(c, "aimcp_model", text="")
        row.operator("aimcp.refresh_models", text="↻", icon='FILE_REFRESH')
        row = box.row(align=True)
        row.prop(c, "aimcp_provider", text="Provider")
        row.enabled = False

        # Suggestions
        box.label(text="Suggestions:", icon='INFO')
        suggestions = getattr(c, "aimcp_model_suggestions", "")
        if suggestions:
            box.label(text=suggestions, icon='BLANK1')

        # Status
        L.separator()
        status = getattr(c, "aimcp_status", "")
        if status:
            L.label(text=status, icon='INFO')

# ─── 3D View Panel (Chat) ───
class PN_PT_Chat(Panel):
    bl_label = "MCP AI Chat"
    bl_idname = "PN_PT_Chat"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'AI'

    def draw(self, ctx):
        L = self.layout
        c = ctx.scene

        # Status + actions
        row = L.row(align=True)
        if getattr(c, "aimcp_connected", False):
            row.operator("aimcp.disconnect", text="Disconnect", icon='X')
            model_name = getattr(c, "aimcp_model", "?")
            row.label(text=f"Online [{model_name}]", icon='CHECKBOX_HLT')
        else:
            row.operator("aimcp.refresh_models", text="Connect", icon='ADD')
            row.label(text="Offline", icon='CHECKBOX_DEHLT')
        row.separator()
        row.operator("aimcp.capture", text="", icon='CAMERA_DATA')
        row.operator("aimcp.export_glb", text="", icon='EXPORT')

        # Chat scroll
        L.separator()
        chat = getattr(c, "aimcp_chat", None)
        if chat and chat.count > 0:
            row = L.row()
            row.template_list("MCP_UL_Chat", "", chat, "msgs", c, "aimcp_chat_index", rows=max(5, chat.count))
        else:
            L.label(text="No messages. Connect and send a message.")

        # Input
        L.separator()
        row = L.row(align=True)
        row.scale_y = 3.0
        row.prop(c, "aimcp_input", text="")
        row = L.row(align=True)
        row.scale_y = 1.5
        row.operator("aimcp.send", text="Send to AI", icon='PLAY')
        row.operator("aimcp.clear", text="Clear", icon='X')

# ─── Operators ───
class OP_CheckConnection(Operator):
    bl_idname = "aimcp.check_connection"; bl_label = "Check Connection"
    bl_description = "Test connection to blender-mcp server"
    def execute(self, ctx):
        host = ctx.scene.aimcp_server_host
        port = ctx.scene.aimcp_server_port
        try:
            r = urllib.request.urlopen(f"http://{host}:{port}/api/health", timeout=3)
            data = json.loads(r.read())
            ctx.scene.aimcp_connected = True
            ctx.scene.aimcp_status = f"Connected. {data.get('models_count', 0)} models available."
            if ctx.area: ctx.area.tag_redraw()
            self.report({'INFO'}, "Connected to server")
        except Exception as e:
            ctx.scene.aimcp_connected = False
            ctx.scene.aimcp_status = f"Connection failed: {str(e)[:60]}"
            if ctx.area: ctx.area.tag_redraw()
            self.report({'ERROR'}, f"Connection failed: {str(e)[:60]}")
        return {'FINISHED'}

class OP_RefreshModels(Operator):
    bl_idname = "aimcp.refresh_models"; bl_label = "Refresh Models"
    bl_description = "Load available models from server and test connection"
    def execute(self, ctx):
        host = ctx.scene.aimcp_server_host
        port = ctx.scene.aimcp_server_port
        try:
            r = urllib.request.urlopen(f"http://{host}:{port}/api/health", timeout=3)
            data = json.loads(r.read())
            ctx.scene.aimcp_connected = True
            ctx.scene.aimcp_status = f"Connected."
            ctx.scene.aimcp_model_suggestions = "Type any model from opencode (Claude, GPT, DeepSeek, etc.)"
            if ctx.area: ctx.area.tag_redraw()
            self.report({'INFO'}, "Connected to server")
        except Exception as e:
            ctx.scene.aimcp_connected = False
            ctx.scene.aimcp_status = f"Failed: {str(e)[:60]}"
            if ctx.area: ctx.area.tag_redraw()
            self.report({'ERROR'}, str(e)[:60])
        return {'FINISHED'}

class OP_Disconnect(Operator):
    bl_idname = "aimcp.disconnect"; bl_label = "Disconnect"
    def execute(self, ctx):
        ctx.scene.aimcp_connected = False
        ctx.scene.aimcp_status = "Disconnected"
        if ctx.area: ctx.area.tag_redraw()
        return {'FINISHED'}

class OP_Send(Operator):
    bl_idname = "aimcp.send"; bl_label = "Send"
    bl_description = "Send message to AI and get response"
    def execute(self, ctx):
        txt = ctx.scene.aimcp_input.strip()
        if not txt: return {'CANCELLED'}
        ctx.scene.aimcp_chat.add("user", txt)
        ctx.scene.aimcp_input = ""
        ctx.scene.aimcp_status = "Processing..."
        if ctx.area: ctx.area.tag_redraw()

        # Send to HTTP bridge
        if ctx.scene.aimcp_connected:
            result = http_post("/api/chat", {
                "message": txt,
                "model": ctx.scene.aimcp_model,
            })
            if "response" in result:
                ctx.scene.aimcp_chat.add("assistant", result["response"])
            elif "error" in result:
                ctx.scene.aimcp_chat.add("assistant", f"Error: {result['error'][:100]}")
            else:
                ctx.scene.aimcp_chat.add("assistant", "Response received.")
        else:
            ctx.scene.aimcp_chat.add("assistant", "Not connected. Click Connect first.")

        ctx.scene.aimcp_status = ""
        ctx.scene.aimcp_chat_index = ctx.scene.aimcp_chat.count - 1
        if ctx.area: ctx.area.tag_redraw()
        return {'FINISHED'}

class OP_Capture(Operator):
    bl_idname = "aimcp.capture"; bl_label = "Capture Scene"
    def execute(self, ctx):
        n = len(bpy.data.objects)
        m = sum(1 for o in bpy.data.objects if o.type == 'MESH')
        ctx.scene.aimcp_chat.add("system", f"Scene: {n} objects, {m} meshes")
        ctx.scene.aimcp_chat_index = ctx.scene.aimcp_chat.count - 1
        if ctx.area: ctx.area.tag_redraw()
        return {'FINISHED'}

class OP_Export(Operator):
    bl_idname = "aimcp.export_glb"; bl_label = "Export GLB"
    def execute(self, ctx):
        out = os.path.expanduser("~/blender-mcp/models/scene.glb")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.export_scene.gltf(filepath=out, export_format='GLB')
        ctx.scene.aimcp_chat.add("system", f"Exported ✅")
        ctx.scene.aimcp_chat_index = ctx.scene.aimcp_chat.count - 1
        if ctx.area: ctx.area.tag_redraw()
        return {'FINISHED'}

class OP_Clear(Operator):
    bl_idname = "aimcp.clear"; bl_label = "Clear"
    def execute(self, ctx):
        ctx.scene.aimcp_chat.clear_all()
        if ctx.area: ctx.area.tag_redraw()
        return {'FINISHED'}

# ─── Register ───
classes = [
    ChatMsg, ChatData, MCP_UL_Chat,
    OP_CheckConnection, OP_RefreshModels, OP_Disconnect, OP_Send,
    OP_Capture, OP_Export, OP_Clear,
    PN_PT_Config, PN_PT_Chat,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.aimcp_chat = PointerProperty(type=ChatData)
    bpy.types.Scene.aimcp_input = StringProperty(name="", description="Describe what to create...")
    bpy.types.Scene.aimcp_connected = BoolProperty(name="", default=False)
    bpy.types.Scene.aimcp_chat_index = IntProperty(name="", default=0)
    bpy.types.Scene.aimcp_server_host = StringProperty(name="", default="localhost")
    bpy.types.Scene.aimcp_server_port = IntProperty(name="", default=9877, min=1024, max=65535)
    bpy.types.Scene.aimcp_model = StringProperty(name="", default="claude-sonnet-4-5",
        description="Model name as configured in opencode (e.g. claude-sonnet-4-5, gpt-4o, deepseek-chat)")
    bpy.types.Scene.aimcp_provider = StringProperty(name="Provider", default="opencode")
    bpy.types.Scene.aimcp_status = StringProperty(name="", default="")
    bpy.types.Scene.aimcp_model_suggestions = StringProperty(name="", default="")

def unregister():
    for cls in reversed(classes):
        try: bpy.utils.unregister_class(cls)
        except: pass
    for attr in ["aimcp_model_suggestions", "aimcp_status", "aimcp_provider", "aimcp_model", "aimcp_server_port",
                 "aimcp_server_host", "aimcp_chat_index", "aimcp_connected",
                 "aimcp_input", "aimcp_chat"]:
        if hasattr(bpy.types.Scene, attr):
            try: delattr(bpy.types.Scene, attr)
            except: pass

if __name__ == "__main__":
    register()
