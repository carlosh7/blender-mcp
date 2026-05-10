# blender-mcp — AI Assistant for Blender v0.7.0
# Panels: Config (Properties) + Chat (3D View Sidebar) + HTTP bridge
# Features: Model selector with providers, search, scrollable list, OpenRouter live API
bl_info = {
    "name": "AI Assistant (blender-mcp)",
    "author": "carlosh7",
    "version": (0, 7, 1),
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

# ─── Model Selector Types ───
class ModelItem(PropertyGroup):
    model_id: StringProperty(name="Model ID")
    model_name: StringProperty(name="Model Name")
    provider: StringProperty(name="Provider")
    context_length: IntProperty(name="Context", default=0)
    pricing: StringProperty(name="Pricing", default="?")

class ProviderItem(PropertyGroup):
    prov_id: StringProperty(name="Provider ID")
    prov_name: StringProperty(name="Provider Name")
    connected: BoolProperty(name="Connected", default=False)
    model_count: IntProperty(name="Models", default=0)
    expanded: BoolProperty(name="Expanded", default=False)
    public_api: BoolProperty(name="Public API", default=False)

class ModelsData(PropertyGroup):
    items: CollectionProperty(type=ModelItem)
    count: IntProperty(name="Count", default=0)
    def add_model(self, mid, mname, prov, ctx_len=0, pricing="?"):
        m = self.items.add()
        m.model_id = mid
        m.model_name = mname
        m.provider = prov
        m.context_length = ctx_len or 0
        m.pricing = pricing or "?"
        self.count = len(self.items)
    def clear_all(self):
        while self.items: self.items.remove(0)
        self.count = 0

class ProvidersData(PropertyGroup):
    items: CollectionProperty(type=ProviderItem)
    count: IntProperty(name="Count", default=0)
    def add_provider(self, pid, pname, connected, count, public_api):
        p = self.items.add()
        p.prov_id = pid
        p.prov_name = pname
        p.connected = connected
        p.model_count = count
        p.public_api = public_api
        self.count = len(self.items)
    def clear_all(self):
        while self.items: self.items.remove(0)
        self.count = 0

# ─── Scrollable Model List (UIList) ───
class MCP_UL_Models(UIList):
    bl_idname = "MCP_UL_Models"
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        current = context.scene.aimcp_model
        is_current = item.model_id == current
        row = layout.row(align=True)
        icon_val = 'RADIOBUT_ON' if is_current else 'RADIOBUT_OFF'
        row.prop(item, "model_id", text="", emboss=False, icon=icon_val)
        name = item.model_name[:50] if item.model_name else item.model_id.split("/")[-1][:50]
        row.label(text=name)
        if is_current:
            row.label(text="", icon='CHECKMARK')

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

        # Model selector with providers
        L.separator()
        box = L.box()
        box.label(text="AI Model", icon='SETTINGS')

        # Current model display
        current_model = getattr(c, "aimcp_model", "not set")
        row = box.row(align=True)
        row.label(text=f"Current: {current_model}", icon='FILE_TICK')
        row.operator("aimcp.refresh_providers", text="", icon='FILE_REFRESH')

        # Show if current provider is connected or not
        prov_connected = getattr(c, "aimcp_current_provider_connected", False)
        if current_model and current_model != "not set":
            prov_name = current_model.split("/")[0] if "/" in current_model else "?"
            if not prov_connected:
                box.label(text=f"⚠ {prov_name}: no API key configured", icon='ERROR')
            else:
                box.label(text=f"✓ {prov_name}: connected", icon='CHECKMARK')

        # Search field
        row = box.row(align=True)
        row.prop(c, "aimcp_model_search", text="", icon='VIEWZOOM')
        if c.aimcp_model_search:
            row.operator("aimcp.clear_search", text="", icon='X')

        # Manual model input (always available)
        row = box.row(align=True)
        row.prop(c, "aimcp_model_text", text="")

        # Provider sections + model list (only connected providers)
        providers = getattr(c, "aimcp_providers_data", None)
        if providers and providers.count > 0:
            for i, prov in enumerate(providers.items):
                prov_box = box.box()
                lbl = f"{prov.prov_name} ({prov.model_count} models)"
                row = prov_box.row(align=True)
                row.label(text=lbl, icon='CHECKBOX_HLT')
                if prov.public_api:
                    row.operator("aimcp.fetch_models", text="Fetch", icon='URL').provider_id = prov.prov_id
                else:
                    row.operator("aimcp.fetch_models", text="Show", icon='DOWNARROW_HLT').provider_id = prov.prov_id

                # If models are loaded for this provider, show them
                models = getattr(c, "aimcp_models_data", None)
                if models and models.count > 0:
                    first_prov = models.items[0].provider if models.count > 0 else ""
                    if first_prov == prov.prov_id:
                        row = prov_box.row()
                        row.template_list("MCP_UL_Models", f"models_{prov.prov_id}",
                            models, "items", c, "aimcp_model_list_index",
                            rows=min(8, models.count))
                        row = prov_box.row(align=True)
                        row.operator("aimcp.apply_selected_model", text="Apply Selected Model", icon='CHECKMARK')
                        if models.count > 50:
                            row = prov_box.row()
                            row.label(text=f"Showing {min(models.count, 50)} of {models.count} models", icon='INFO')
        else:
            if prov_connected:
                box.label(text="Click ↻ to detect provider models", icon='BLANK1')
            else:
                box.label(text="No providers connected. Type a model name manually.", icon='INFO')

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
            row.operator("aimcp.check_connection", text="Connect", icon='ADD')
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
            ctx.scene.aimcp_status = f"Failed: {str(e)[:60]}"
            if ctx.area: ctx.area.tag_redraw()
            self.report({'ERROR'}, f"Connection failed: {str(e)[:60]}")
        return {'FINISHED'}

class OP_RefreshProviders(Operator):
    bl_idname = "aimcp.refresh_providers"; bl_label = "↻ Refresh Providers"
    bl_description = "Detect providers from opencode config and fetch model lists"
    def execute(self, ctx):
        host = ctx.scene.aimcp_server_host
        port = ctx.scene.aimcp_server_port
        try:
            # Fetch providers
            r = urllib.request.urlopen(f"http://{host}:{port}/api/providers", timeout=5)
            data = json.loads(r.read())
            ctx.scene.aimcp_connected = True

            # Update current model and provider
            if data.get("current_model"):
                ctx.scene.aimcp_model = data["current_model"]
            ctx.scene.aimcp_current_provider_connected = data.get("current_provider_connected", False)

            # Build providers list (only connected providers)
            prov_data = ctx.scene.aimcp_providers_data
            prov_data.clear_all()
            for p in data.get("providers", []):
                prov_data.add_provider(
                    p["id"], p["name"],
                    True,  # all in list are connected
                    p.get("model_count", 0),
                    p.get("public_api", False),
                )

            # Auto-fetch models for connected non-OpenRouter providers
            models_data = ctx.scene.aimcp_models_data
            models_data.clear_all()
            for p in data.get("providers", []):
                if not p.get("public_api"):
                    try:
                        r2 = urllib.request.urlopen(
                            f"http://{host}:{port}/api/models-list?provider={p['id']}", timeout=5)
                        mdata = json.loads(r2.read())
                        for m in mdata.get("models", []):
                            models_data.add_model(
                                m["id"], m.get("name", m["id"]),
                                m.get("provider", p["id"]),
                                m.get("context_length", 0),
                                m.get("pricing", "?"),
                            )
                    except: pass

            ctx.scene.aimcp_status = f"Providers: {prov_data.count} detected"
            if ctx.area: ctx.area.tag_redraw()
            self.report({'INFO'}, f"Providers refreshed: {prov_data.count}")
        except Exception as e:
            ctx.scene.aimcp_connected = False
            ctx.scene.aimcp_status = f"Failed: {str(e)[:60]}"
            if ctx.area: ctx.area.tag_redraw()
            self.report({'ERROR'}, str(e)[:60])
        return {'FINISHED'}

class OP_FetchModels(Operator):
    bl_idname = "aimcp.fetch_models"; bl_label = "Fetch Models"
    bl_description = "Fetch models for a specific provider"
    provider_id: StringProperty(default="")
    def execute(self, ctx):
        host = ctx.scene.aimcp_server_host
        port = ctx.scene.aimcp_server_port
        prov = self.provider_id
        if not prov:
            self.report({'ERROR'}, "No provider specified")
            return {'CANCELLED'}
        try:
            ctx.scene.aimcp_status = f"Loading models for {prov}..."
            if ctx.area: ctx.area.tag_redraw()

            r = urllib.request.urlopen(
                f"http://{host}:{port}/api/models-list?provider={prov}&page_size=200", timeout=15)
            data = json.loads(r.read())

            models_data = ctx.scene.aimcp_models_data
            models_data.clear_all()
            search = ctx.scene.aimcp_model_search.lower()

            for m in data.get("models", []):
                mid = m["id"]
                if search and search not in mid.lower() and search not in m.get("name", mid).lower():
                    continue
                models_data.add_model(
                    mid, m.get("name", mid),
                    m.get("provider", prov),
                    m.get("context_length", 0),
                    m.get("pricing", "?"),
                )

            total = data.get("total", models_data.count)
            ctx.scene.aimcp_status = f"{models_data.count} of {total} models loaded for {prov}"
            ctx.scene.aimcp_model_list_index = 0
            if ctx.area: ctx.area.tag_redraw()
            self.report({'INFO'}, f"{models_data.count} models loaded for {prov}")
        except Exception as e:
            ctx.scene.aimcp_status = f"Error loading models: {str(e)[:60]}"
            if ctx.area: ctx.area.tag_redraw()
            self.report({'ERROR'}, str(e)[:60])
        return {'FINISHED'}

class OP_ApplySelectedModel(Operator):
    bl_idname = "aimcp.apply_selected_model"; bl_label = "Apply Model"
    bl_description = "Set the selected model as active and save to opencode config"
    def execute(self, ctx):
        models_data = ctx.scene.aimcp_models_data
        idx = ctx.scene.aimcp_model_list_index
        if idx < 0 or idx >= models_data.count:
            self.report({'ERROR'}, "No model selected")
            return {'CANCELLED'}
        model_item = models_data.items[idx]
        model_id = model_item.model_id

        # Set locally
        ctx.scene.aimcp_model = model_id

        # Save to opencode config via HTTP bridge
        host = ctx.scene.aimcp_server_host
        port = ctx.scene.aimcp_server_port
        try:
            body = json.dumps({"model": model_id}).encode()
            req = urllib.request.Request(
                f"http://{host}:{port}/api/set-model",
                data=body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            resp = json.loads(urllib.request.urlopen(req, timeout=5).read())
            if resp.get("success"):
                ctx.scene.aimcp_status = f"Model set to: {model_id}"
                self.report({'INFO'}, f"Model saved: {model_id}")
            else:
                ctx.scene.aimcp_status = f"Model set locally only: {resp.get('error', '?')}"
                self.report({'WARNING'}, f"Local only: {resp.get('error', '?')}")
        except Exception as e:
            ctx.scene.aimcp_status = f"Model set locally: {model_id}"
            self.report({'WARNING'}, f"Local only: {str(e)[:60]}")

        ctx.scene.aimcp_model_list_index = idx
        if ctx.area: ctx.area.tag_redraw()
        return {'FINISHED'}

class OP_ClearSearch(Operator):
    bl_idname = "aimcp.clear_search"; bl_label = "Clear"
    bl_description = "Clear search filter"
    def execute(self, ctx):
        ctx.scene.aimcp_model_search = ""
        if ctx.area: ctx.area.tag_redraw()
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
    ModelItem, ProviderItem, ModelsData, ProvidersData,
    MCP_UL_Models,
    OP_CheckConnection, OP_RefreshProviders, OP_FetchModels,
    OP_ApplySelectedModel, OP_ClearSearch, OP_Disconnect,
    OP_Send, OP_Capture, OP_Export, OP_Clear,
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
    bpy.types.Scene.aimcp_status = StringProperty(name="", default="")
    bpy.types.Scene.aimcp_model_search = StringProperty(name="", default="",
        description="Filter models by name")
    bpy.types.Scene.aimcp_model_list_index = IntProperty(name="", default=0)
    bpy.types.Scene.aimcp_current_provider_connected = BoolProperty(name="", default=False)
    bpy.types.Scene.aimcp_model_text = StringProperty(name="", default="",
        description="Type any model name manually (e.g. openai/gpt-4o)")
    bpy.types.Scene.aimcp_providers_data = PointerProperty(type=ProvidersData)
    bpy.types.Scene.aimcp_models_data = PointerProperty(type=ModelsData)

def unregister():
    for cls in reversed(classes):
        try: bpy.utils.unregister_class(cls)
        except: pass
    for attr in ["aimcp_models_data", "aimcp_providers_data", "aimcp_model_list_index",
                 "aimcp_current_provider_connected", "aimcp_model_text", "aimcp_model_search",
                 "aimcp_status", "aimcp_model", "aimcp_server_port", "aimcp_server_host",
                 "aimcp_chat_index", "aimcp_connected", "aimcp_input", "aimcp_chat"]:
        if hasattr(bpy.types.Scene, attr):
            try: delattr(bpy.types.Scene, attr)
            except: pass

if __name__ == "__main__":
    register()
