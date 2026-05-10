# blender-mcp — AI Assistant for Blender v0.7.2
# Panels: Config (Properties) + Chat (3D View Sidebar) + HTTP bridge
# Models fetched live from provider APIs (DeepSeek, opencode-go, OpenRouter)
bl_info = {
    "name": "AI Assistant (blender-mcp)",
    "author": "carlosh7",
    "version": (0, 7, 2),
    "blender": (4, 0, 0),
    "location": "Properties > Scene > AI Config | View3D > Sidebar (N) > AI Chat",
    "description": "Chat with AI to create 3D models. Config panel in Properties, chat in 3D View sidebar.",
    "doc_url": "https://github.com/carlosh7/blender-mcp",
    "category": "3D View",
}
import bpy, os, json, urllib.request, urllib.error, threading
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

class MCP_UL_Chat(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        tag = "You" if item.role == "user" else "AI" if item.role == "assistant" else "Sys"
        col = layout.column()
        col.scale_y = 1.5
        col.label(text=f"[{tag}]")
        for line in item.text.split("\n"):
            col.label(text=f"  {line[:120]}")

# ─── Model types ───
class ModelItem(PropertyGroup):
    model_id: StringProperty(name="Model ID")
    model_name: StringProperty(name="Model Name")
    provider: StringProperty(name="Provider")

class ModelsData(PropertyGroup):
    items: CollectionProperty(type=ModelItem)
    count: IntProperty(name="Count", default=0)
    def add_model(self, mid, mname, prov):
        m = self.items.add()
        m.model_id = mid; m.model_name = mname; m.provider = prov
        self.count = len(self.items)
    def clear_all(self):
        while self.items: self.items.remove(0)
        self.count = 0

class MCP_UL_Models(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        current = context.scene.aimcp_model
        is_current = item.model_id == current
        row = layout.row(align=True)
        icon_val = 'RADIOBUT_ON' if is_current else 'RADIOBUT_OFF'
        row.prop(item, "model_id", text="", emboss=False, icon=icon_val)
        row.label(text=item.model_name[:60])

# ─── Config Panel ───
class PN_PT_Config(Panel):
    bl_label = "AI Assistant Config"
    bl_idname = "PN_PT_Config"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'scene'

    def draw(self, ctx):
        L = self.layout; c = ctx.scene

        box = L.box()
        box.label(text="Server Connection", icon='LINKED')
        row = box.row(align=True)
        row.prop(c, "aimcp_server_host", text="")
        row.prop(c, "aimcp_server_port", text="")
        row = box.row(align=True)
        if getattr(c, "aimcp_connected", False):
            row.label(text="Online", icon='CHECKBOX_HLT')
        else:
            row.label(text="Offline", icon='CHECKBOX_DEHLT')
        row.operator("aimcp.check_connection", text="Check")

        L.separator()
        box = L.box()
        box.label(text="AI Model", icon='SETTINGS')
        current = getattr(c, "aimcp_model", "")
        box.label(text=f"Current: {current}" if current else "Current: (not set)")
        row = box.row(align=True)
        row.operator("aimcp.refresh_all", text="Refresh all providers", icon='FILE_REFRESH')
        if getattr(c, "aimcp_refreshing", False):
            row.label(text="", icon='SORTTIME')

        row = box.row(align=True)
        row.prop(c, "aimcp_model_search", text="", icon='VIEWZOOM')

        models_data = getattr(c, "aimcp_models_data", None)
        if models_data and models_data.count > 0:
            search = c.aimcp_model_search.lower()
            # Count visible
            visible = 0
            for m in models_data.items:
                if not search or search in m.model_id.lower() or search in m.model_name.lower():
                    visible += 1
            rows = min(12, max(3, visible))
            row = box.row()
            row.template_list("MCP_UL_Models", "", models_data, "items",
                c, "aimcp_model_list_index", rows=rows)
            row = box.row(align=True)
            row.operator("aimcp.apply_selected_model", text="Apply", icon='CHECKMARK')
            row.operator("aimcp.clear_search", text="Clear", icon='X')
        else:
            box.label(text="Click 'Refresh all providers' to load models")

        L.separator()
        status = getattr(c, "aimcp_status", "")
        if status:
            L.label(text=status, icon='INFO')

# ─── Chat Panel ───
class PN_PT_Chat(Panel):
    bl_label = "MCP AI Chat"
    bl_idname = "PN_PT_Chat"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'AI'

    def draw(self, ctx):
        L = self.layout; c = ctx.scene

        row = L.row(align=True)
        if getattr(c, "aimcp_connected", False):
            row.operator("aimcp.disconnect", text="Disconnect", icon='X')
            row.label(text=f"Online [{getattr(c, 'aimcp_model', '?')}]", icon='CHECKBOX_HLT')
        else:
            row.operator("aimcp.check_connection", text="Connect", icon='ADD')
            row.label(text="Offline", icon='CHECKBOX_DEHLT')
        row.separator()
        row.operator("aimcp.capture", text="", icon='CAMERA_DATA')
        row.operator("aimcp.export_glb", text="", icon='EXPORT')

        L.separator()
        chat = getattr(c, "aimcp_chat", None)
        if chat and chat.count > 0:
            row = L.row()
            row.template_list("MCP_UL_Chat", "", chat, "msgs", c, "aimcp_chat_index", rows=max(5, chat.count))
        else:
            L.label(text="No messages. Connect and send a message.")

        L.separator()
        row = L.row(align=True); row.scale_y = 3.0; row.prop(c, "aimcp_input", text="")
        row = L.row(align=True); row.scale_y = 1.5
        row.operator("aimcp.send", text="Send to AI", icon='PLAY')
        row.operator("aimcp.clear", text="Clear", icon='X')

# ─── Operators ───
class OP_CheckConnection(Operator):
    bl_idname = "aimcp.check_connection"; bl_label = "Check Connection"
    def execute(self, ctx):
        host = ctx.scene.aimcp_server_host; port = ctx.scene.aimcp_server_port
        try:
            r = urllib.request.urlopen(f"http://{host}:{port}/api/health", timeout=3)
            json.loads(r.read())
            ctx.scene.aimcp_connected = True
            # Also fetch current model from opencode config
            try:
                r2 = urllib.request.urlopen(f"http://{host}:{port}/api/providers", timeout=3)
                pdata = json.loads(r2.read())
                if pdata.get("current_model"):
                    ctx.scene.aimcp_model = pdata["current_model"]
            except: pass
            ctx.scene.aimcp_status = f"Connected."
            if ctx.area: ctx.area.tag_redraw()
            self.report({'INFO'}, "Connected")
        except Exception as e:
            ctx.scene.aimcp_connected = False
            ctx.scene.aimcp_status = f"Failed: {str(e)[:60]}"
            if ctx.area: ctx.area.tag_redraw()
            self.report({'ERROR'}, str(e)[:60])
        return {'FINISHED'}

class OP_RefreshAll(Operator):
    bl_idname = "aimcp.refresh_all"; bl_label = "Refresh All"
    bl_description = "Detect connected providers and fetch all models from their APIs"
    _timer = None

    def execute(self, ctx):
        host = ctx.scene.aimcp_server_host; port = ctx.scene.aimcp_server_port
        ctx.scene.aimcp_refreshing = True
        ctx.scene.aimcp_status = "Refreshing providers..."
        if ctx.area: ctx.area.tag_redraw()

        def fetch():
            try:
                req = urllib.request.Request(f"http://{host}:{port}/api/fetch-all-models",
                    data=json.dumps({"force": True}).encode(),
                    headers={"Content-Type": "application/json"}, method="POST")
                r = urllib.request.urlopen(req, timeout=30)
                data = json.loads(r.read())
                providers_data = data.get("providers", {})

                # Collect all models from all providers
                all_models = []
                provider_names = []
                for pid, result in providers_data.items():
                    provider_names.append(pid)
                    for m in result.get("models", []):
                        all_models.append(m)

                # Update in main thread
                def update():
                    md = ctx.scene.aimcp_models_data
                    md.clear_all()
                    for m in all_models:
                        md.add_model(m["id"], m.get("name", m["id"]), m.get("provider", "?"))
                    ctx.scene.aimcp_model_list_index = 0
                    ctx.scene.aimcp_status = f"Models: {md.count} (from {', '.join(provider_names)})"
                    ctx.scene.aimcp_refreshing = False
                    if ctx.area: ctx.area.tag_redraw()
                bpy.app.timers.register(update, first_interval=0.01)
            except Exception as e:
                def update_err():
                    ctx.scene.aimcp_status = f"Refresh error: {str(e)[:80]}"
                    ctx.scene.aimcp_refreshing = False
                    if ctx.area: ctx.area.tag_redraw()
                bpy.app.timers.register(update_err, first_interval=0.01)

        threading.Thread(target=fetch, daemon=True).start()
        return {'FINISHED'}

class OP_ApplySelectedModel(Operator):
    bl_idname = "aimcp.apply_selected_model"; bl_label = "Apply"
    bl_description = "Set selected model and save to opencode config"
    def execute(self, ctx):
        md = ctx.scene.aimcp_models_data
        idx = ctx.scene.aimcp_model_list_index
        if idx < 0 or idx >= md.count:
            self.report({'ERROR'}, "No model selected"); return {'CANCELLED'}
        model_id = md.items[idx].model_id
        ctx.scene.aimcp_model = model_id
        host = ctx.scene.aimcp_server_host; port = ctx.scene.aimcp_server_port
        try:
            body = json.dumps({"model": model_id}).encode()
            req = urllib.request.Request(f"http://{host}:{port}/api/set-model",
                data=body, headers={"Content-Type": "application/json"}, method="POST")
            resp = json.loads(urllib.request.urlopen(req, timeout=5).read())
            if resp.get("success"):
                ctx.scene.aimcp_status = f"Model: {model_id}"
                self.report({'INFO'}, f"Model set: {model_id}")
            else:
                self.report({'WARNING'}, f"Local only: {resp.get('error','?')}")
        except Exception as e:
            self.report({'WARNING'}, f"Local: {str(e)[:60]}")
        ctx.scene.aimcp_model_list_index = idx
        if ctx.area: ctx.area.tag_redraw()
        return {'FINISHED'}

class OP_ClearSearch(Operator):
    bl_idname = "aimcp.clear_search"; bl_label = "Clear"
    def execute(self, ctx):
        ctx.scene.aimcp_model_search = ""
        if ctx.area: ctx.area.tag_redraw()
        return {'FINISHED'}

class OP_Disconnect(Operator):
    bl_idname = "aimcp.disconnect"; bl_label = "Disconnect"
    def execute(self, ctx):
        ctx.scene.aimcp_connected = False; ctx.scene.aimcp_status = ""
        if ctx.area: ctx.area.tag_redraw(); return {'FINISHED'}

class OP_Send(Operator):
    bl_idname = "aimcp.send"; bl_label = "Send"
    def execute(self, ctx):
        txt = ctx.scene.aimcp_input.strip()
        if not txt: return {'CANCELLED'}
        ctx.scene.aimcp_chat.add("user", txt)
        ctx.scene.aimcp_input = ""
        ctx.scene.aimcp_status = "Processing..."
        if ctx.area: ctx.area.tag_redraw()

        if ctx.scene.aimcp_connected:
            result = http_post("/api/chat", {"message": txt, "model": ctx.scene.aimcp_model})
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
    bl_idname = "aimcp.capture"; bl_label = "Capture"
    def execute(self, ctx):
        n = len(bpy.data.objects); m = sum(1 for o in bpy.data.objects if o.type == 'MESH')
        ctx.scene.aimcp_chat.add("system", f"Scene: {n} objects, {m} meshes")
        ctx.scene.aimcp_chat_index = ctx.scene.aimcp_chat.count - 1
        if ctx.area: ctx.area.tag_redraw(); return {'FINISHED'}

class OP_Export(Operator):
    bl_idname = "aimcp.export_glb"; bl_label = "Export"
    def execute(self, ctx):
        out = os.path.expanduser("~/blender-mcp/models/scene.glb")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.export_scene.gltf(filepath=out, export_format='GLB')
        ctx.scene.aimcp_chat.add("system", "Exported")
        ctx.scene.aimcp_chat_index = ctx.scene.aimcp_chat.count - 1
        if ctx.area: ctx.area.tag_redraw(); return {'FINISHED'}

class OP_Clear(Operator):
    bl_idname = "aimcp.clear"; bl_label = "Clear"
    def execute(self, ctx):
        ctx.scene.aimcp_chat.clear_all()
        if ctx.area: ctx.area.tag_redraw(); return {'FINISHED'}

# ─── Register ───
classes = [
    ChatMsg, ChatData, MCP_UL_Chat,
    ModelItem, ModelsData, MCP_UL_Models,
    OP_CheckConnection, OP_RefreshAll, OP_ApplySelectedModel, OP_ClearSearch,
    OP_Disconnect, OP_Send, OP_Capture, OP_Export, OP_Clear,
    PN_PT_Config, PN_PT_Chat,
]

def register():
    for cls in classes: bpy.utils.register_class(cls)
    bpy.types.Scene.aimcp_chat = PointerProperty(type=ChatData)
    bpy.types.Scene.aimcp_input = StringProperty(name="", description="Describe what to create...")
    bpy.types.Scene.aimcp_connected = BoolProperty(name="", default=False)
    bpy.types.Scene.aimcp_chat_index = IntProperty(name="", default=0)
    bpy.types.Scene.aimcp_refreshing = BoolProperty(name="", default=False)
    bpy.types.Scene.aimcp_server_host = StringProperty(name="", default="localhost")
    bpy.types.Scene.aimcp_server_port = IntProperty(name="", default=9877, min=1024, max=65535)
    bpy.types.Scene.aimcp_model = StringProperty(name="", default="")
    bpy.types.Scene.aimcp_status = StringProperty(name="", default="")
    bpy.types.Scene.aimcp_model_search = StringProperty(name="", default="")
    bpy.types.Scene.aimcp_model_list_index = IntProperty(name="", default=0)
    bpy.types.Scene.aimcp_models_data = PointerProperty(type=ModelsData)

def unregister():
    for cls in reversed(classes):
        try: bpy.utils.unregister_class(cls)
        except: pass
    for attr in ["aimcp_models_data", "aimcp_model_list_index", "aimcp_model_search",
                 "aimcp_refreshing", "aimcp_status", "aimcp_model", "aimcp_server_port",
                 "aimcp_server_host", "aimcp_chat_index", "aimcp_connected",
                 "aimcp_input", "aimcp_chat"]:
        if hasattr(bpy.types.Scene, attr):
            try: delattr(bpy.types.Scene, attr)
            except: pass

if __name__ == "__main__":
    register()
