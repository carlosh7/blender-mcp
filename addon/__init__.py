# blender-mcp — AI Assistant for Blender v0.7.4
# Panels: Config (Properties) + Chat (3D View Sidebar)
# Models fetched live from provider APIs in separate sections
bl_info = {
    "name": "AI Assistant (blender-mcp)",
    "author": "carlosh7",
    "version": (0, 7, 4),
    "blender": (4, 0, 0),
    "location": "Properties > Scene > AI Config | View3D > Sidebar (N) > AI Chat",
    "description": "Chat with AI to create 3D models via connected provider APIs.",
    "doc_url": "https://github.com/carlosh7/blender-mcp",
    "category": "3D View",
}
import bpy, os, json, urllib.request, threading
from bpy.types import Panel, Operator, PropertyGroup
from bpy.props import StringProperty, IntProperty, BoolProperty, PointerProperty, CollectionProperty

HTTP_HOST = "http://localhost:9877"

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

# ─── Chat ───
class ChatMsg(PropertyGroup):
    role: StringProperty(name="Role"); text: StringProperty(name="Text")

class ChatData(PropertyGroup):
    msgs: CollectionProperty(type=ChatMsg); count: IntProperty(default=0)
    def add(self, r, t): m = self.msgs.add(); m.role = r; m.text = t; self.count = len(self.msgs)
    def clear_all(self):
        while self.msgs: self.msgs.remove(0); self.count = 0

# ─── Model ───
class ModelItem(PropertyGroup):
    model_id: StringProperty(); model_name: StringProperty(); provider: StringProperty()

class ModelsData(PropertyGroup):
    items: CollectionProperty(type=ModelItem); count: IntProperty(default=0)
    def add(self, mid, name, prov):
        m = self.items.add(); m.model_id = mid; m.model_name = name; m.provider = prov; self.count = len(self.items)
    def clear_all(self):
        while self.items: self.items.remove(0); self.count = 0
    def by_provider(self, prov):
        return [m for m in self.items if m.provider == prov]

PROVIDER_ORDER = ["deepseek", "opencode-go", "openrouter"]
PROVIDER_LABELS = {"deepseek": "DeepSeek", "opencode-go": "OpenCode Go", "openrouter": "OpenRouter"}
PROVIDER_ICONS = {"deepseek": 'DOT', "opencode-go": 'DOT', "openrouter": 'URL'}

# ─── Config Panel ───
class PN_PT_Config(Panel):
    bl_label = "AI Assistant Config"; bl_idname = "PN_PT_Config"
    bl_space_type = 'PROPERTIES'; bl_region_type = 'WINDOW'; bl_context = 'scene'

    def draw(self, ctx):
        L = self.layout; c = ctx.scene
        box = L.box()
        box.label(text="Server", icon='LINKED')
        row = box.row(align=True)
        row.prop(c, "aimcp_host", text=""); row.prop(c, "aimcp_port", text="")
        row = box.row(align=True)
        if c.aimcp_connected: row.label(text="Online", icon='CHECKBOX_HLT')
        else: row.label(text="Offline", icon='CHECKBOX_DEHLT')
        row.operator("aimcp.check", text="Check")

        L.separator()
        box = L.box()
        box.label(text="AI Model", icon='SETTINGS')
        current = c.aimcp_model
        box.label(text=f"Current: {current}" if current else "Current: (none)")
        row = box.row(align=True)
        row.operator("aimcp.refresh", text="Refresh all", icon='FILE_REFRESH')
        if c.aimcp_refreshing: row.label(text="", icon='SORTTIME')

        # Provider sections
        md = c.aimcp_models
        if md and md.count > 0:
            for prov_id in PROVIDER_ORDER:
                prov_models = [m for m in md.items if m.provider == prov_id]
                if not prov_models: continue
                count = len(prov_models)
                prov_box = box.box()
                label = PROVIDER_LABELS.get(prov_id, prov_id)
                row = prov_box.row(align=True)
                row.label(text=f"{label} ({count})", icon=PROVIDER_ICONS.get(prov_id, 'DOT'))

                # Search per provider
                search_key = f"aimcp_search_{prov_id.replace('-','_')}"
                search_val = getattr(c, search_key, "")
                row = prov_box.row(align=True)
                row.prop(c, search_key, text="", icon='VIEWZOOM')
                if search_val:
                    row.operator("aimcp.clear_search", text="", icon='X').search_prop = search_key

                # Model rows
                s = search_val.lower()
                visible = [m for m in prov_models if not s or s in m.model_id.lower() or s in m.model_name.lower()]
                for m in visible:
                    row = prov_box.row(align=True)
                    if m.model_id == current:
                        row.label(text="", icon='RADIOBUT_ON')
                        row.label(text=f"{m.model_name}  [{m.model_id}]")
                    else:
                        op = row.operator("aimcp.select", text=m.model_name, icon='RADIOBUT_OFF')
                        op.model_id = m.model_id
                        op.provider = prov_id

                if len(prov_models) > 20:
                    prov_box.label(text=f"Showing {len(visible)} of {len(prov_models)}")

                row = prov_box.row(align=True)
                if visible:
                    first_vis = visible[0]
                    row.operator("aimcp.apply_model", text=f"Apply {PROVIDER_LABELS.get(prov_id,prov_id)}", icon='CHECKMARK').model_id = first_vis.model_id
        else:
            box.label(text="Click 'Refresh all' to load models from your APIs")

        L.separator()
        status = c.aimcp_status
        if status: L.label(text=status, icon='INFO')

# ─── Chat Panel ───
class PN_PT_Chat(Panel):
    bl_label = "MCP AI Chat"; bl_idname = "PN_PT_Chat"
    bl_space_type = 'VIEW_3D'; bl_region_type = 'UI'; bl_category = 'AI'
    def draw(self, ctx):
        L = self.layout; c = ctx.scene
        row = L.row(align=True)
        if c.aimcp_connected:
            row.operator("aimcp.disconnect", text="Disconnect", icon='X')
            m = c.aimcp_model or "?"
            row.label(text=f"Online [{m}]", icon='CHECKBOX_HLT')
        else:
            row.operator("aimcp.check", text="Connect", icon='ADD')
            row.label(text="Offline", icon='CHECKBOX_DEHLT')
        row.separator()
        row.operator("aimcp.capture", text="", icon='CAMERA_DATA')
        row.operator("aimcp.export", text="", icon='EXPORT')
        L.separator()
        chat = c.aimcp_chat
        if chat and chat.count > 0:
            L.operator("aimcp.show_chat", text=f"Chat ({chat.count} messages)", icon='DOT')
            L.operator("aimcp.clear_chat", text="Clear chat", icon='X')
        else:
            L.label(text="No messages.")
        L.separator()
        row = L.row(align=True); row.scale_y = 3.0; row.prop(c, "aimcp_input", text="")
        row = L.row(align=True); row.scale_y = 1.5
        row.operator("aimcp.send", text="Send to AI", icon='PLAY')
        row.operator("aimcp.clear_chat", text="Clear", icon='X')

# ─── Operators ───
class OP_Check(Operator):
    bl_idname = "aimcp.check"; bl_label = "Check Connection"
    def execute(self, ctx):
        h = ctx.scene.aimcp_host; p = ctx.scene.aimcp_port
        try:
            r = urllib.request.urlopen(f"http://{h}:{p}/api/health", timeout=3)
            json.loads(r.read())
            ctx.scene.aimcp_connected = True
            try:
                r2 = urllib.request.urlopen(f"http://{h}:{p}/api/providers", timeout=3)
                d = json.loads(r2.read())
                if d.get("current_model"): ctx.scene.aimcp_model = d["current_model"]
            except: pass
            ctx.scene.aimcp_status = "Connected"
            if ctx.area: ctx.area.tag_redraw()
        except Exception as e:
            ctx.scene.aimcp_connected = False
            ctx.scene.aimcp_status = f"Failed: {str(e)[:60]}"
            if ctx.area: ctx.area.tag_redraw()
        return {'FINISHED'}

class OP_Refresh(Operator):
    bl_idname = "aimcp.refresh"; bl_label = "Refresh"
    def execute(self, ctx):
        h = ctx.scene.aimcp_host; p = ctx.scene.aimcp_port
        ctx.scene.aimcp_refreshing = True
        ctx.scene.aimcp_status = "Refreshing..."
        if ctx.area: ctx.area.tag_redraw()
        def fetch():
            try:
                req = urllib.request.Request(f"http://{h}:{p}/api/fetch-all-models",
                    data=json.dumps({"force": True}).encode(),
                    headers={"Content-Type": "application/json"}, method="POST")
                r = urllib.request.urlopen(req, timeout=30)
                data = json.loads(r.read())["providers"]
                def update():
                    md = ctx.scene.aimcp_models
                    md.clear_all()
                    names = []
                    for pid, result in data.items():
                        names.append(pid)
                        for m in result.get("models", []):
                            md.add(m["id"], m.get("name", m["id"]), pid)
                    ctx.scene.aimcp_status = f"{md.count} models loaded"
                    ctx.scene.aimcp_refreshing = False
                    if ctx.area: ctx.area.tag_redraw()
                bpy.app.timers.register(update, first_interval=0.01)
            except Exception as e:
                def err():
                    ctx.scene.aimcp_status = f"Error: {str(e)[:80]}"
                    ctx.scene.aimcp_refreshing = False
                    if ctx.area: ctx.area.tag_redraw()
                bpy.app.timers.register(err, first_interval=0.01)
        threading.Thread(target=fetch, daemon=True).start()
        return {'FINISHED'}

class OP_SelectModel(Operator):
    bl_idname = "aimcp.select"; bl_label = "Select"
    model_id: StringProperty(); provider: StringProperty()
    def execute(self, ctx):
        ctx.scene.aimcp_model = self.model_id
        ctx.scene.aimcp_status = f"Selected: {self.model_id}"
        if ctx.area: ctx.area.tag_redraw()
        return {'FINISHED'}

class OP_ApplyModel(Operator):
    bl_idname = "aimcp.apply_model"; bl_label = "Apply"
    model_id: StringProperty()
    def execute(self, ctx):
        mid = self.model_id
        ctx.scene.aimcp_model = mid
        h = ctx.scene.aimcp_host; p = ctx.scene.aimcp_port
        try:
            body = json.dumps({"model": mid}).encode()
            req = urllib.request.Request(f"http://{h}:{p}/api/set-model",
                data=body, headers={"Content-Type": "application/json"}, method="POST")
            r = json.loads(urllib.request.urlopen(req, timeout=5).read())
            if r.get("success"):
                ctx.scene.aimcp_status = f"Saved: {mid}"
            else:
                ctx.scene.aimcp_status = f"Local: {mid}"
        except Exception as e:
            ctx.scene.aimcp_status = f"Local: {mid}"
        if ctx.area: ctx.area.tag_redraw()
        return {'FINISHED'}

class OP_ClearSearch(Operator):
    bl_idname = "aimcp.clear_search"; bl_label = "Clear"
    search_prop: StringProperty()
    def execute(self, ctx):
        if self.search_prop and hasattr(ctx.scene, self.search_prop):
            setattr(ctx.scene, self.search_prop, "")
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
            r = http_post("/api/chat", {"message": txt, "model": ctx.scene.aimcp_model})
            if "response" in r: ctx.scene.aimcp_chat.add("assistant", r["response"])
            elif "error" in r: ctx.scene.aimcp_chat.add("assistant", f"Error: {r['error'][:100]}")
            else: ctx.scene.aimcp_chat.add("assistant", "Done")
        else:
            ctx.scene.aimcp_chat.add("assistant", "Not connected")
        ctx.scene.aimcp_status = ""
        if ctx.area: ctx.area.tag_redraw()
        return {'FINISHED'}

class OP_Capture(Operator):
    bl_idname = "aimcp.capture"; bl_label = "Capture"
    def execute(self, ctx):
        n = len(bpy.data.objects); m = sum(1 for o in bpy.data.objects if o.type == 'MESH')
        ctx.scene.aimcp_chat.add("system", f"Scene: {n} objects, {m} meshes")
        if ctx.area: ctx.area.tag_redraw(); return {'FINISHED'}

class OP_Export(Operator):
    bl_idname = "aimcp.export"; bl_label = "Export"
    def execute(self, ctx):
        out = os.path.expanduser("~/blender-mcp/models/scene.glb")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.export_scene.gltf(filepath=out, export_format='GLB')
        ctx.scene.aimcp_chat.add("system", "Exported")
        if ctx.area: ctx.area.tag_redraw(); return {'FINISHED'}

class OP_ClearChat(Operator):
    bl_idname = "aimcp.clear_chat"; bl_label = "Clear"
    def execute(self, ctx):
        ctx.scene.aimcp_chat.clear_all()
        if ctx.area: ctx.area.tag_redraw(); return {'FINISHED'}

class OP_ShowChat(Operator):
    bl_idname = "aimcp.show_chat"; bl_label = "Show Chat"
    def execute(self, ctx):
        chat = ctx.scene.aimcp_chat
        for m in chat.msgs:
            print(f"[{m.role}] {m.text[:100]}")
        return {'FINISHED'}

# ─── Register ───
classes = [
    ChatMsg, ChatData,
    ModelItem, ModelsData,
    OP_Check, OP_Refresh, OP_SelectModel, OP_ApplyModel, OP_ClearSearch,
    OP_Disconnect, OP_Send, OP_Capture, OP_Export, OP_ClearChat, OP_ShowChat,
    PN_PT_Config, PN_PT_Chat,
]

def register():
    for cls in classes: bpy.utils.register_class(cls)
    bpy.types.Scene.aimcp_chat = PointerProperty(type=ChatData)
    bpy.types.Scene.aimcp_input = StringProperty(default="")
    bpy.types.Scene.aimcp_connected = BoolProperty(default=False)
    bpy.types.Scene.aimcp_refreshing = BoolProperty(default=False)
    bpy.types.Scene.aimcp_host = StringProperty(default="localhost")
    bpy.types.Scene.aimcp_port = IntProperty(default=9877, min=1024, max=65535)
    bpy.types.Scene.aimcp_model = StringProperty(default="")
    bpy.types.Scene.aimcp_status = StringProperty(default="")
    bpy.types.Scene.aimcp_models = PointerProperty(type=ModelsData)
    # Search per provider
    for pid in PROVIDER_ORDER:
        key = f"aimcp_search_{pid.replace('-','_')}"
        setattr(bpy.types.Scene, key, StringProperty(default=""))
    # Auto-load current model from opencode config
    try:
        r = urllib.request.urlopen(f"http://localhost:9877/api/providers", timeout=2)
        d = json.loads(r.read())
        if d.get("current_model"):
            from bpy.app import timers
            def set_model():
                for s in bpy.data.scenes:
                    s.aimcp_model = d["current_model"]
                return None
            timers.register(set_model, first_interval=0.5)
    except: pass

def unregister():
    for cls in reversed(classes):
        try: bpy.utils.unregister_class(cls)
        except: pass
    attrs = ["aimcp_models", "aimcp_status", "aimcp_model", "aimcp_port", "aimcp_host",
             "aimcp_refreshing", "aimcp_connected", "aimcp_input", "aimcp_chat"]
    for pid in PROVIDER_ORDER:
        attrs.append(f"aimcp_search_{pid.replace('-','_')}")
    for a in attrs:
        if hasattr(bpy.types.Scene, a):
            try: delattr(bpy.types.Scene, a)
            except: pass

if __name__ == "__main__":
    register()
