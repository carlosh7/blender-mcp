# blender-mcp — AI Assistant for Blender v0.8.1
# Panels: Config (Properties) + Chat (3D View Sidebar)
# AI chat via MCP tools (read-chat / respond-chat)
bl_info = {
    "name": "AI Assistant (blender-mcp)",
    "author": "carlosh7",
    "version": (0, 8, 1),
    "blender": (4, 0, 0),
    "location": "Properties > Scene > AI Config | View3D > Sidebar (N) > AI Chat",
    "description": "Chat with AI to create 3D models via connected provider APIs.",
    "doc_url": "https://github.com/carlosh7/blender-mcp",
    "category": "3D View",
}
import bpy, os, json, time, urllib.request, threading
from bpy.types import Panel, Operator, PropertyGroup, UIList
from bpy.props import StringProperty, IntProperty, BoolProperty, PointerProperty, CollectionProperty

HTTP_HOST = "http://localhost:9877"
_poll_results = {}  # {message_id: {"response": "...", "error": ""} or None if still polling}

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
        r = urllib.request.urlopen(req, timeout=180)
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

class MCP_UL_Chat(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        tag = "You" if item.role == "user" else "AI" if item.role == "assistant" else "Sys"
        col = layout.column()
        col.scale_y = 1.5
        col.label(text=f"[{tag}]")
        for line in item.text.split("\n"):
            col.label(text=f"  {line[:150]}")

# ─── Model ───
class ModelItem(PropertyGroup):
    model_id: StringProperty(); model_name: StringProperty(); provider: StringProperty()

class ModelsData(PropertyGroup):
    items: CollectionProperty(type=ModelItem); count: IntProperty(default=0)
    def add(self, mid, name, prov):
        m = self.items.add(); m.model_id = mid; m.model_name = name; m.provider = prov; self.count = len(self.items)
    def clear_all(self):
        while self.items: self.items.remove(0); self.count = 0

PROVIDER_ORDER = ["deepseek", "opencode-go", "openrouter"]
PROVIDER_LABELS = {"deepseek": "DeepSeek", "opencode-go": "OpenCode Go", "openrouter": "OpenRouter"}

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

        md = c.aimcp_models
        if md and md.count > 0:
            for prov_id in PROVIDER_ORDER:
                prov_models = [m for m in md.items if m.provider == prov_id]
                if not prov_models: continue
                count = len(prov_models)
                prov_box = box.box()
                label = PROVIDER_LABELS.get(prov_id, prov_id)
                row = prov_box.row(align=True)
                row.label(text=f"{label} ({count})", icon='DOT')

                search_key = f"aimcp_search_{prov_id.replace('-','_')}"
                search_val = getattr(c, search_key, "")
                row = prov_box.row(align=True)
                row.prop(c, search_key, text="", icon='VIEWZOOM')
                if search_val:
                    row.operator("aimcp.clear_search", text="", icon='X').search_prop = search_key

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

                if len(prov_models) > 20:
                    prov_box.label(text=f"Showing {len(visible)} of {len(prov_models)}")

                if visible:
                    row = prov_box.row(align=True)
                    row.operator("aimcp.apply_model", text=f"Apply {PROVIDER_LABELS.get(prov_id,prov_id)}", icon='CHECKMARK').model_id = visible[0].model_id
        else:
            box.label(text="Click 'Refresh all' to load models")

        L.separator()
        status = c.aimcp_status
        if status: L.label(text=status, icon='INFO')

# ─── Chat Panel ───
class PN_PT_Chat(Panel):
    bl_label = "MCP AI Chat"; bl_idname = "PN_PT_Chat"
    bl_space_type = 'VIEW_3D'; bl_region_type = 'UI'; bl_category = 'AI'

    def draw(self, ctx):
        L = self.layout; c = ctx.scene

        # Status bar
        row = L.row(align=True)
        if c.aimcp_connected:
            row.operator("aimcp.disconnect", text="", icon='X')
            m = c.aimcp_model or "?"
            row.label(text=f"Online [{m}]", icon='CHECKBOX_HLT')
        else:
            row.operator("aimcp.check", text="Connect", icon='ADD')
            row.label(text="Offline", icon='CHECKBOX_DEHLT')
        row.separator()
        row.operator("aimcp.capture", text="", icon='CAMERA_DATA')
        row.operator("aimcp.export", text="", icon='EXPORT')

        L.separator()
        # Chat messages with scroll
        chat = c.aimcp_chat
        if chat and chat.count > 0:
            row = L.row()
            row.template_list("MCP_UL_Chat", "", chat, "msgs", c, "aimcp_chat_index",
                rows=min(15, max(8, chat.count)))
        else:
            L.label(text="No messages. Type something and send.")

        L.separator()
        # Input
        row = L.row(align=True)
        row.scale_y = 3.0
        row.prop(c, "aimcp_input", text="")
        row = L.row(align=True)
        row.scale_y = 1.5
        cns = row.operator("aimcp.send", text="Send to AI", icon='PLAY')
        cns.connected = c.aimcp_connected
        row.operator("aimcp.clear_chat", text="Clear", icon='X')
        if c.aimcp_waiting:
            L.label(text="Waiting for AI response...", icon='SORTTIME')

# ─── Operators ───
class OP_Check(Operator):
    bl_idname = "aimcp.check"; bl_label = "Check Connection"
    def execute(self, ctx):
        ctx.scene.aimcp_status = "Connecting..."
        if ctx.area: ctx.area.tag_redraw()
        h = ctx.scene.aimcp_host; p = ctx.scene.aimcp_port
        def check():
            try:
                r = urllib.request.urlopen(f"http://{h}:{p}/api/health", timeout=3)
                json.loads(r.read())
                ctx.scene.aimcp_connected = True
                try:
                    r2 = urllib.request.urlopen(f"http://{h}:{p}/api/providers", timeout=3)
                    d = json.loads(r2.read())
                    if d.get("current_model"): ctx.scene.aimcp_model = d["current_model"]
                except: pass
                def ok():
                    ctx.scene.aimcp_status = "Connected"
                    if ctx.area: ctx.area.tag_redraw()
                bpy.app.timers.register(ok, first_interval=0.01)
            except Exception as e:
                def fail():
                    ctx.scene.aimcp_connected = False
                    ctx.scene.aimcp_status = f"Failed: {str(e)[:60]}"
                    if ctx.area: ctx.area.tag_redraw()
                bpy.app.timers.register(fail, first_interval=0.01)
        threading.Thread(target=check, daemon=True).start()
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
    model_id: StringProperty()
    def execute(self, ctx):
        ctx.scene.aimcp_model = self.model_id
        ctx.scene.aimcp_status = f"Selected: {self.model_id}"
        if ctx.area: ctx.area.tag_redraw(); return {'FINISHED'}

class OP_ApplyModel(Operator):
    bl_idname = "aimcp.apply_model"; bl_label = "Apply"
    model_id: StringProperty()
    def execute(self, ctx):
        mid = self.model_id
        ctx.scene.aimcp_model = mid
        ctx.scene.aimcp_status = "Saving..."
        if ctx.area: ctx.area.tag_redraw()
        h = ctx.scene.aimcp_host; p = ctx.scene.aimcp_port
        def save():
            try:
                body = json.dumps({"model": mid}).encode()
                req = urllib.request.Request(f"http://{h}:{p}/api/set-model",
                    data=body, headers={"Content-Type": "application/json"}, method="POST")
                r = json.loads(urllib.request.urlopen(req, timeout=5).read())
                msg = "Saved: " + mid if r.get("success") else "Local: " + mid
                def ok():
                    ctx.scene.aimcp_status = msg
                    if ctx.area: ctx.area.tag_redraw()
                bpy.app.timers.register(ok, first_interval=0.01)
            except:
                def err():
                    ctx.scene.aimcp_status = "Local: " + mid
                    if ctx.area: ctx.area.tag_redraw()
                bpy.app.timers.register(err, first_interval=0.01)
        threading.Thread(target=save, daemon=True).start()
        return {'FINISHED'}

class OP_ClearSearch(Operator):
    bl_idname = "aimcp.clear_search"; bl_label = "Clear"
    search_prop: StringProperty()
    def execute(self, ctx):
        if self.search_prop and hasattr(ctx.scene, self.search_prop):
            setattr(ctx.scene, self.search_prop, "")
        if ctx.area: ctx.area.tag_redraw(); return {'FINISHED'}

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
        ctx.scene.aimcp_status = "Waiting..."
        ctx.scene.aimcp_waiting = True
        ctx.scene.aimcp_chat_index = ctx.scene.aimcp_chat.count - 1
        ctx.scene.aimcp_pending_msg_id = ""
        if ctx.area: ctx.area.tag_redraw()

        h = ctx.scene.aimcp_host; p = ctx.scene.aimcp_port

        def send():
            result = http_post("/api/chat", {"message": txt})
            if result and result.get("message_id"):
                mid = result["message_id"]
                ctx.scene.aimcp_pending_msg_id = mid
                _poll_results[mid] = None  # still polling

                # Background poll thread (no UI blocking)
                def poll_worker():
                    while _poll_results.get(mid) is None:
                        try:
                            r = urllib.request.urlopen(
                                f"http://{h}:{p}/api/chat/status?message_id={mid}", timeout=3)
                            status = json.loads(r.read())
                            if status.get("status") in ("done", "error", "not_found"):
                                _poll_results[mid] = status
                                return
                        except:
                            pass
                        time.sleep(2)

                threading.Thread(target=poll_worker, daemon=True).start()

                # UI timer — only checks _poll_results, never does HTTP
                def check():
                    mid = ctx.scene.aimcp_pending_msg_id
                    if not mid:
                        return None
                    result = _poll_results.get(mid)
                    if result is None:
                        return 1.0  # check again in 1s
                    # Result ready
                    resp = result.get("response", "")
                    ctx.scene.aimcp_chat.add("assistant", resp)
                    ctx.scene.aimcp_chat_index = ctx.scene.aimcp_chat.count - 1
                    ctx.scene.aimcp_status = ""
                    ctx.scene.aimcp_waiting = False
                    ctx.scene.aimcp_pending_msg_id = ""
                    _poll_results.pop(mid, None)
                    if ctx.area: ctx.area.tag_redraw()
                    return None

                bpy.app.timers.register(check, first_interval=0.5)
            else:
                def err():
                    ctx.scene.aimcp_waiting = False
                    ctx.scene.aimcp_status = "Send failed"
                    if ctx.area: ctx.area.tag_redraw()
                bpy.app.timers.register(err, first_interval=0.01)

        threading.Thread(target=send, daemon=True).start()
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

# ─── Register ───
classes = [
    ChatMsg, ChatData, MCP_UL_Chat,
    ModelItem, ModelsData,
    OP_Check, OP_Refresh, OP_SelectModel, OP_ApplyModel, OP_ClearSearch,
    OP_Disconnect, OP_Send, OP_Capture, OP_Export, OP_ClearChat,
    PN_PT_Config, PN_PT_Chat,
]

def register():
    for cls in classes: bpy.utils.register_class(cls)
    bpy.types.Scene.aimcp_chat = PointerProperty(type=ChatData)
    bpy.types.Scene.aimcp_input = StringProperty(default="")
    bpy.types.Scene.aimcp_connected = BoolProperty(default=False)
    bpy.types.Scene.aimcp_refreshing = BoolProperty(default=False)
    bpy.types.Scene.aimcp_waiting = BoolProperty(default=False)
    bpy.types.Scene.aimcp_pending_msg_id = StringProperty(default="")
    bpy.types.Scene.aimcp_chat_index = IntProperty(default=0)
    bpy.types.Scene.aimcp_host = StringProperty(default="localhost")
    bpy.types.Scene.aimcp_port = IntProperty(default=9877, min=1024, max=65535)
    bpy.types.Scene.aimcp_model = StringProperty(default="")
    bpy.types.Scene.aimcp_status = StringProperty(default="")
    bpy.types.Scene.aimcp_models = PointerProperty(type=ModelsData)
    for pid in ["deepseek", "opencode-go", "openrouter"]:
        key = f"aimcp_search_{pid.replace('-','_')}"
        setattr(bpy.types.Scene, key, StringProperty(default=""))

def unregister():
    for cls in reversed(classes):
        try: bpy.utils.unregister_class(cls)
        except: pass
    attrs = ["aimcp_models", "aimcp_status", "aimcp_model", "aimcp_port", "aimcp_host",
             "aimcp_pending_msg_id", "aimcp_chat_index", "aimcp_waiting", "aimcp_refreshing",
             "aimcp_connected", "aimcp_input", "aimcp_chat"]
    for pid in ["deepseek", "opencode-go", "openrouter"]:
        attrs.append(f"aimcp_search_{pid.replace('-','_')}")
    for a in attrs:
        if hasattr(bpy.types.Scene, a):
            try: delattr(bpy.types.Scene, a)
            except: pass

if __name__ == "__main__":
    register()
