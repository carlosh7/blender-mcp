"""
blender-mcp-ultra v7.0 — AI Assistant PRO (OpenCode Server Connection)
Connects to local OpenCode server at localhost:4096.
"""

import json
import os
import urllib.request
from datetime import datetime

import bpy
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    EnumProperty,
    FloatProperty,
    IntProperty,
    StringProperty,
)
from bpy.types import Operator, Panel, PropertyGroup

bl_info = {
    "name": "AI Assistant PRO",
    "blender": (4, 0, 0),
    "category": "3D View",
    "version": (7, 0, 0),
    "author": "CarlosH",
    "description": "Professional AI assistant - Connects to OpenCode server",
}


# ═══════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".blender_mcp")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
HISTORY_FILE = os.path.join(CONFIG_DIR, "chat_history.json")

# OpenCode server
OPENCODE_SERVER = "http://localhost:4096"


def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_config(config):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return []


def save_history(messages):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    data = [
        {"role": m.role, "content": m.content, "timestamp": m.timestamp} for m in messages[-100:]
    ]
    with open(HISTORY_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ═══════════════════════════════════════════════════════════════
# PROPERTIES
# ═══════════════════════════════════════════════════════════════


class AIMessage(PropertyGroup):
    role: StringProperty(default="user")
    content: StringProperty(default="")
    timestamp: StringProperty(default="")


class AIModelItem(PropertyGroup):
    name: StringProperty(default="")
    is_free: BoolProperty(default=False)
    cost_in: FloatProperty(default=0.0)
    cost_out: FloatProperty(default=0.0)
    context_length: IntProperty(default=0)


class AIProps(PropertyGroup):
    # Chat
    chat_messages: CollectionProperty(type=AIMessage)
    chat_input: StringProperty(default="")
    attached_image: StringProperty(default="", subtype="FILE_PATH")
    has_image: BoolProperty(default=False)

    # Connection
    is_connected: BoolProperty(default=False)
    server_url: StringProperty(default="http://localhost:4096")

    # Provider
    provider: EnumProperty(
        name="Provider",
        items=[
            ("opencode_go", "OpenCode Go", "OpenCode Go models"),
            ("opencode_zen", "OpenCode Zen", "OpenCode Zen models"),
            ("ollama", "Ollama (Local)", "Free, runs locally"),
        ],
        default="opencode_go",
    )

    # Selected model
    selected_model: StringProperty(default="")

    # Available models
    available_models: CollectionProperty(type=AIModelItem)

    # Settings
    temperature: FloatProperty(default=0.7, min=0.0, max=2.0)
    max_tokens: IntProperty(default=2048, min=256, max=8192)
    auto_execute: BoolProperty(default=True)
    language: EnumProperty(items=[("en", "English", ""), ("es", "Español", "")], default="en")

    # Voice
    voice_enabled: BoolProperty(default=False)

    # Status
    status: StringProperty(default="Ready")


# ═══════════════════════════════════════════════════════════════
# OPENCODE SERVER CONNECTION
# ═══════════════════════════════════════════════════════════════


def api_request(url, headers=None, data=None, timeout=30):
    """Make API request."""
    try:
        req = urllib.request.Request(
            url, data=data, headers=headers or {}, method="POST" if data else "GET"
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode()[:200]
        except Exception:
            pass
        return {"error": f"HTTP {e.code}: {e.reason} - {body}"}
    except Exception as e:
        return {"error": str(e)}


def fetch_ollama_models(url):
    """Fetch models from Ollama local server."""
    result = api_request(f"{url}/api/tags")
    if "error" in result:
        return [], result["error"]
    models = []
    for m in result.get("models", []):
        models.append(
            {"name": m["name"], "is_free": True, "cost_in": 0, "cost_out": 0, "context_length": 0}
        )
    return models, None


def check_server():
    """Check if OpenCode server is running."""
    try:
        req = urllib.request.Request(f"{OPENCODE_SERVER}/global/health")
        with urllib.request.urlopen(req, timeout=2) as resp:
            result = json.loads(resp.read().decode())
            return True, result
    except Exception:
        return False, None


def fetch_models_from_server(provider_type):
    """Fetch models from OpenCode server."""
    # Try to get provider info from server
    try:
        req = urllib.request.Request(f"{OPENCODE_SERVER}/provider")
        with urllib.request.urlopen(req, timeout=5) as resp:
            result = json.loads(resp.read().decode())

            models = []
            providers = result.get("all", [])

            for prov in providers:
                prov_id = prov.get("id", "")
                if provider_type.replace("_", "-") in prov_id or provider_type in prov_id:
                    for model_id, model_data in prov.get("models", {}).items():
                        models.append(
                            {
                                "name": model_id,
                                "is_free": model_data.get("free", False),
                                "cost_in": model_data.get("costIn", 0),
                                "cost_out": model_data.get("costOut", 0),
                                "context_length": model_data.get("context_length", 0),
                            }
                        )

            return models, None
    except Exception as e:
        return [], str(e)


def generate_via_server(prompt, provider, model):
    """Generate response via OpenCode server or Ollama directly."""

    # Handle Ollama directly (no server needed)
    if provider == "ollama":
        try:
            ollama_url = "http://localhost:11434"
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
            }
            result = api_request(
                f"{ollama_url}/api/chat",
                data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"},
            )
            if "error" in result:
                return f"Error: {result['error']}"
            return result.get("message", {}).get("content", "No response")
        except Exception as e:
            return f"Error: {str(e)}"

    # Handle OpenCode providers via server
    try:
        # Create session
        session_result = api_request(
            f"{OPENCODE_SERVER}/session",
            data=json.dumps({"title": "Blender AI Assistant"}).encode(),
            headers={"Content-Type": "application/json"},
        )

        if "error" in session_result:
            return f"Error creating session: {session_result['error']}"

        session_id = session_result.get("id")
        if not session_id:
            return "Error: No session ID"

        # Send message
        message_result = api_request(
            f"{OPENCODE_SERVER}/session/{session_id}/message",
            data=json.dumps(
                {
                    "parts": [{"type": "text", "text": prompt}],
                    "model": {"providerID": provider.replace("_", "-"), "modelID": model},
                }
            ).encode(),
            headers={"Content-Type": "application/json"},
        )

        if "error" in message_result:
            return f"Error: {message_result['error']}"

        # Extract response
        parts = message_result.get("parts", [])
        for part in parts:
            if part.get("type") == "text":
                return part.get("text", "No response")

        return "No response"

    except Exception as e:
        return f"Error: {str(e)}"


# ═══════════════════════════════════════════════════════════════
# CODE EXECUTION
# ═══════════════════════════════════════════════════════════════


def exec_code(code):
    try:
        exec(code, {"bpy": bpy, "__builtins__": __builtins__})
        return "✅ Done"
    except Exception as e:
        return f"❌ Error: {e}"


# ═══════════════════════════════════════════════════════════════
# LOCAL COMMANDS
# ═══════════════════════════════════════════════════════════════


def try_local(msg, props):
    m = msg.lower().strip()

    if any(w in m for w in ["create", "make", "add", "crear", "hacer"]):
        if "chair" in m or "silla" in m:
            return (
                "🪑 Creating chair...",
                """bpy.ops.mesh.primitive_cube_add(size=1, location=(0,0,0.45)); s=bpy.context.active_object; s.name="Chair"; s.scale=(0.45,0.45,0.04); mat=bpy.data.materials.new("Wood"); mat.use_nodes=True; b=mat.node_tree.nodes.get("Principled BSDF"); b.inputs["Base Color"].default_value=(0.4,0.25,0.12,1); b.inputs["Roughness"].default_value=0.7; s.data.materials.append(mat)
for x in [-0.18,0.18]:
 for y in [-0.18,0.18]:
  bpy.ops.mesh.primitive_cylinder_add(radius=0.02,depth=0.45,location=(x,y,0.22)); bpy.context.active_object.data.materials.append(mat)
print("Chair created")""",
            )
        elif "table" in m or "mesa" in m:
            return (
                "🪑 Creating table...",
                """bpy.ops.mesh.primitive_cube_add(size=1, location=(0,0,0.75)); t=bpy.context.active_object; t.name="Table"; t.scale=(1.2,0.8,0.04); mat=bpy.data.materials.new("Wood"); mat.use_nodes=True; b=mat.node_tree.nodes.get("Principled BSDF"); b.inputs["Base Color"].default_value=(0.3,0.18,0.08,1); t.data.materials.append(mat)
for x in [-0.5,0.5]:
 for y in [-0.3,0.3]:
  bpy.ops.mesh.primitive_cylinder_add(radius=0.03,depth=0.75,location=(x,y,0.375)); bpy.context.active_object.data.materials.append(mat)
print("Table created")""",
            )
        elif "lamp" in m or "luz" in m:
            return (
                "💡 Creating lamp...",
                """bpy.ops.mesh.primitive_cylinder_add(radius=0.15,depth=0.03,location=(0,0,0.015)); bpy.context.active_object.name="Base"
bpy.ops.mesh.primitive_cylinder_add(radius=0.018,depth=0.2,location=(0,0,0.13)); bpy.context.active_object.name="Column"
bpy.ops.object.light_add(type='POINT',location=(0,0,0.35)); bpy.context.active_object.data.energy=50
print("Lamp created")""",
            )
        elif "cube" in m:
            return (
                "📦",
                "bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,0.5)); bpy.context.active_object.name='Cube'; print('Cube')",
            )
        elif "sphere" in m:
            return (
                "🔵",
                "bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5,location=(0,0,0.5)); bpy.context.active_object.name='Sphere'; print('Sphere')",
            )
        elif "cylinder" in m:
            return (
                "🔵",
                "bpy.ops.mesh.primitive_cylinder_add(radius=0.5,depth=1,location=(0,0,0.5)); bpy.context.active_object.name='Cylinder'; print('Cylinder')",
            )
        elif "cone" in m or "cono" in m:
            return (
                "🔺",
                "bpy.ops.mesh.primitive_cone_add(radius1=0.5,depth=1,location=(0,0,0.5)); bpy.context.active_object.name='Cone'; print('Cone')",
            )
        elif "torus" in m or "donut" in m:
            return (
                "🍩",
                "bpy.ops.mesh.primitive_torus_add(major_radius=0.5,minor_radius=0.2,location=(0,0,0.5)); bpy.context.active_object.name='Torus'; print('Torus')",
            )
        elif "plane" in m or "plano" in m:
            return (
                "📐",
                "bpy.ops.mesh.primitive_plane_add(size=2,location=(0,0,0)); bpy.context.active_object.name='Plane'; print('Plane')",
            )

    if any(w in m for w in ["delete", "remove", "borrar", "eliminar"]):
        return (
            "🗑️",
            "bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(); print('Deleted')",
        )

    if any(w in m for w in ["color", "paint", "colorear"]):
        c = (0.8, 0.8, 0.8)
        if "red" in m or "rojo" in m:
            c = (0.8, 0.1, 0.1)
        elif "blue" in m or "azul" in m:
            c = (0.1, 0.1, 0.8)
        elif "green" in m or "verde" in m:
            c = (0.1, 0.7, 0.1)
        elif "yellow" in m or "amarillo" in m:
            c = (0.9, 0.9, 0.1)
        elif "black" in m or "negro" in m:
            c = (0.05, 0.05, 0.05)
        elif "white" in m or "blanco" in m:
            c = (0.95, 0.95, 0.95)
        return (
            "🎨",
            f"o=bpy.context.active_object\nif o and o.type=='MESH':\n m=o.data.materials[0] if o.data.materials else bpy.data.materials.new('Mat'); o.data.materials.append(m) if not o.data.materials else None\n m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=({c[0]},{c[1]},{c[2]},1)\n print('Color applied')\nelse: print('Select mesh')",
        )

    if any(w in m for w in ["material", "wood", "madera", "metal", "glass", "vidrio"]):
        p = "wood"
        if "metal" in m:
            p = "metal"
        elif "glass" in m or "vidrio" in m:
            p = "glass"
        pr = {
            "wood": (0.45, 0.30, 0.15, 0.7, 0.0),
            "metal": (0.85, 0.65, 0.10, 0.1, 1.0),
            "glass": (0.95, 0.95, 0.95, 0.0, 0.0),
        }
        v = pr.get(p, pr["wood"])
        return (
            "🪵",
            f"o=bpy.context.active_object\nif o and o.type=='MESH':\n m=o.data.materials[0] if o.data.materials else bpy.data.materials.new('{p}'); o.data.materials.append(m) if not o.data.materials else None\n bs=m.node_tree.nodes.get('Principled BSDF')\n bs.inputs['Base Color'].default_value=({v[0]},{v[1]},{v[2]},1)\n bs.inputs['Roughness'].default_value={v[3]}; bs.inputs['Metallic'].default_value={v[4]}\n print('Material applied')\nelse: print('Select mesh')",
        )

    if any(w in m for w in ["undo", "desacer", "volver"]):
        return "⏪", "bpy.ops.ed.undo(); print('Undo')"
    if any(w in m for w in ["redo", "rehacer"]):
        return "⏩", "bpy.ops.ed.redo(); print('Redo')"

    if (
        "export" in m
        or "save" in m
        or "exportar" in m
        or "guardar" in m
        or "download" in m
        or "descargar" in m
    ):
        fmt = "glb"
        if "fbx" in m:
            fmt = "fbx"
        elif "obj" in m:
            fmt = "obj"
        elif "stl" in m:
            fmt = "stl"
        return (
            "📤",
            f"import os; fp=os.path.join(os.path.expanduser('~'),'Desktop',f'export.{{'{fmt}'}}'); bpy.ops.object.select_all(action='SELECT')\ntry:\n if '{fmt}'=='glb': bpy.ops.export_scene.gltf(filepath=fp,export_format='GLB')\n elif '{fmt}'=='fbx': bpy.ops.export_scene.fbx(filepath=fp)\n elif '{fmt}'=='obj': bpy.ops.export_scene.obj(filepath=fp)\n elif '{fmt}'=='stl': bpy.ops.export_mesh.stl(filepath=fp)\n print(f'Exported to {{fp}}')\nexcept Exception as e: print(f'{{e}}')",
        )

    if "status" in m or "estado" in m or "info" in m:
        return (
            "📊",
            "print(f'Objects: {len(bpy.context.scene.objects)} | Materials: {len(bpy.data.materials)}')",
        )
    if "clean" in m or "limpiar" in m:
        return (
            "🧹",
            "bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(); print('Cleaned')",
        )
    if any(w in m for w in ["help", "ayuda", "commands", "comandos"]):
        return "📚", None

    return None


def get_help(lang="en"):
    if lang == "es":
        return "📚 COMANDOS:\n• crear silla/mesa/lámpara/cubo/esfera\n• eliminar todo\n• color rojo/azul/verde\n• aplicar madera/metal/vidrio\n• deshacer/rehacer\n• exportar como glb/fbx/obj/stl\n• estado / limpiar"
    return "📚 COMMANDS:\n• create chair/table/lamp/cube/sphere\n• delete all\n• color red/blue/green\n• apply wood/metal/glass\n• undo / redo\n• export as glb/fbx/obj/stl\n• status / clean"


# ═══════════════════════════════════════════════════════════════
# OPERATORS
# ═══════════════════════════════════════════════════════════════


class AI_OT_Send(Operator):
    bl_idname = "ai.send"
    bl_label = "Send"

    def execute(self, context):
        props = context.scene.ai_props
        if not props.chat_input and not props.has_image:
            return {"CANCELLED"}

        user_msg = props.chat_input
        if props.has_image:
            user_msg = f"[Image: {os.path.basename(props.attached_image)}] {user_msg}"

        msg = props.chat_messages.add()
        msg.role = "user"
        msg.content = user_msg
        msg.timestamp = datetime.now().strftime("%H:%M")

        # Try local first
        result = try_local(props.chat_input, props)
        if result:
            response, code = result
            if code and props.auto_execute:
                output = exec_code(code)
                response += f"\n{output}"
        else:
            # Use OpenCode server
            response = generate_via_server(user_msg, props.provider, props.selected_model)

        msg = props.chat_messages.add()
        msg.role = "assistant"
        msg.content = response
        msg.timestamp = datetime.now().strftime("%H:%M")

        while len(props.chat_messages) > 100:
            props.chat_messages.remove(0)

        save_history(props.chat_messages)
        props.chat_input = ""
        props.has_image = False
        props.attached_image = ""

        return {"FINISHED"}


class AI_OT_Clear(Operator):
    bl_idname = "ai.clear"
    bl_label = "Clear"

    def execute(self, context):
        context.scene.ai_props.chat_messages.clear()
        return {"FINISHED"}


class AI_OT_AttachImage(Operator):
    bl_idname = "ai.attach_image"
    bl_label = "📎"
    filepath: StringProperty(subtype="FILE_PATH")

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        if self.filepath:
            context.scene.ai_props.attached_image = self.filepath
            context.scene.ai_props.has_image = True
            self.report({"INFO"}, f"📎 {os.path.basename(self.filepath)}")
        return {"FINISHED"}


class AI_OT_StartServer(Operator):
    bl_idname = "ai.start_server"
    bl_label = "Start"

    def execute(self, context):
        context.scene.ai_props.is_connected = True
        context.scene.ai_props.status = "Connected"
        self.report({"INFO"}, "Connected")
        return {"FINISHED"}


class AI_OT_StopServer(Operator):
    bl_idname = "ai.stop_server"
    bl_label = "Stop"

    def execute(self, context):
        context.scene.ai_props.is_connected = False
        context.scene.ai_props.status = "Disconnected"
        self.report({"INFO"}, "Disconnected")
        return {"FINISHED"}


class AI_OT_SaveConfig(Operator):
    bl_idname = "ai.save_config"
    bl_label = "Save"

    def execute(self, context):
        p = context.scene.ai_props
        config = {
            "provider": p.provider,
            "selected_model": p.selected_model,
            "server_url": p.server_url,
            "temperature": p.temperature,
            "max_tokens": p.max_tokens,
            "language": p.language,
        }
        try:
            save_config(config)
            self.report({"INFO"}, "✅ Saved")
        except Exception as e:
            self.report({"ERROR"}, f"❌ {e}")
        return {"FINISHED"}


class AI_OT_TestConnection(Operator):
    bl_idname = "ai.test_connection"
    bl_label = "Test"

    def execute(self, context):
        p = context.scene.ai_props
        try:
            # Check server
            server_ok, server_info = check_server()
            if not server_ok:
                self.report({"ERROR"}, "❌ OpenCode server not running. Run 'opencode serve'")
                return {"FINISHED"}

            # Test generation
            r = generate_via_server("Say hello in one word", p.provider, p.selected_model)
            if "Error" in r:
                self.report({"ERROR"}, f"❌ {r}")
            else:
                self.report({"INFO"}, f"✅ OK: {r[:50]}")
        except Exception as e:
            self.report({"ERROR"}, f"❌ {str(e)}")
        return {"FINISHED"}


class AI_OT_FetchModels(Operator):
    bl_idname = "ai.fetch_models"
    bl_label = "Fetch Models"

    def execute(self, context):
        p = context.scene.ai_props
        p.available_models.clear()

        # Only check server for OpenCode providers
        if p.provider in ("opencode_go", "opencode_zen"):
            server_ok, _ = check_server()
            if not server_ok:
                self.report({"ERROR"}, "❌ OpenCode server not running. Run 'opencode serve'")
                return {"FINISHED"}

        try:
            # Fetch from server for OpenCode, or directly for Ollama
            if p.provider in ("opencode_go", "opencode_zen"):
                models, error = fetch_models_from_server(p.provider)
            elif p.provider == "ollama":
                models, error = fetch_ollama_models(p.ollama_url)
            else:
                models, error = [], "Unknown provider"

            if error:
                self.report({"ERROR"}, f"❌ {error}")
                return {"FINISHED"}

            if not models:
                self.report({"WARNING"}, "⚠️ No models found")
                return {"FINISHED"}

            for m in models:
                item = p.available_models.add()
                item.name = m["name"]
                item.is_free = m["is_free"]
                item.cost_in = m.get("cost_in", 0)
                item.cost_out = m.get("cost_out", 0)
                item.context_length = m.get("context_length", 0)

            # Auto-select first model
            if models and not p.selected_model:
                p.selected_model = models[0]["name"]

            free_count = sum(1 for m in models if m["is_free"])
            self.report({"INFO"}, f"✅ {len(models)} models ({free_count} free)")

        except Exception as e:
            self.report({"ERROR"}, f"❌ {str(e)}")

        return {"FINISHED"}


class AI_OT_SelectModel(Operator):
    bl_idname = "ai.select_model"
    bl_label = "Select"

    model_name: StringProperty()

    def execute(self, context):
        context.scene.ai_props.selected_model = self.model_name
        self.report({"INFO"}, f"✅ Selected: {self.model_name}")
        return {"FINISHED"}


class AI_OT_VoiceToggle(Operator):
    bl_idname = "ai.voice_toggle"
    bl_label = "🎤"

    def execute(self, context):
        p = context.scene.ai_props
        p.voice_enabled = not p.voice_enabled
        self.report({"INFO"}, f"Voice: {'ON' if p.voice_enabled else 'OFF'}")
        return {"FINISHED"}


# ═══════════════════════════════════════════════════════════════
# PANELS
# ═══════════════════════════════════════════════════════════════


class AI_PT_Main(Panel):
    bl_label = "🤖 AI Assistant"
    bl_idname = "AI_PT_main"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "AI"

    def draw(self, context):
        layout = self.layout
        p = context.scene.ai_props

        # Check server status
        server_ok, _ = check_server()

        box = layout.box()

        if server_ok and p.selected_model:
            provider_display = p.provider.replace("_", " ").title()
            box.label(text=f"✅ {provider_display} → {p.selected_model}", icon="CHECKMARK")
        elif server_ok:
            box.label(text="✅ OpenCode Server Connected", icon="CHECKMARK")
        else:
            box.label(text="❌ Run 'opencode serve' first", icon="X")

        row = box.row(align=True)
        row.operator("ai.start_server", text="", icon="PLAY")
        row.operator("ai.stop_server", text="", icon="PAUSE")
        row.operator("ai.voice_toggle", text="", icon="PLAY" if p.voice_enabled else "PAUSE")


class AI_PT_Chat(Panel):
    bl_label = "💬 Chat"
    bl_idname = "AI_PT_chat"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "AI"
    bl_parent_id = "AI_PT_main"

    def draw(self, context):
        layout = self.layout
        p = context.scene.ai_props

        box = layout.box()
        if len(p.chat_messages) == 0:
            box.label(text="👋 Hi! Ask me anything.")
            box.label(text="Type 'help' for commands.")
        else:
            start = max(0, len(p.chat_messages) - 8)
            for i in range(start, len(p.chat_messages)):
                msg = p.chat_messages[i]
                if msg.role == "user":
                    box.label(text=f"👤 {msg.content[:70]}")
                else:
                    for line in msg.content.split("\n")[:2]:
                        if line.strip():
                            box.label(text=f"🤖 {line[:70]}")

        if p.has_image:
            box.label(text=f"📎 {os.path.basename(p.attached_image)}", icon="IMAGE_DATA")

        box = layout.box()
        row = box.row(align=True)
        row.operator("ai.attach_image", text="", icon="FILE_IMAGE")
        row.prop(p, "chat_input", text="", placeholder="Type message...")
        row.operator("ai.send", text="", icon="PLAY")
        row.operator("ai.clear", text="", icon="X")


class AI_PT_Settings(Panel):
    bl_label = "⚙️ Settings"
    bl_idname = "AI_PT_settings"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "AI"
    bl_parent_id = "AI_PT_main"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        p = context.scene.ai_props

        # Provider
        box = layout.box()
        box.label(text="Provider:", icon="SETTINGS")
        box.prop(p, "provider", text="")

        # Server URL
        box.prop(p, "server_url", text="Server URL")

        # Fetch button
        box.operator("ai.fetch_models", text="🔄 Fetch Models", icon="FILE_REFRESH")

        # Model dropdown
        if len(p.available_models) > 0:
            box = layout.box()
            box.label(text=f"Models ({len(p.available_models)}):", icon="VIEWZOOM")

            if p.selected_model:
                box.label(text=f"✅ Using: {p.selected_model}", icon="CHECKMARK")

            for i, model in enumerate(p.available_models[:15]):
                row = box.row(align=True)
                free_tag = " [FREE]" if model.is_free else ""
                price = ""
                if not model.is_free and model.cost_in > 0:
                    price = f" ${model.cost_in:.2f}"
                row.label(text=f"{model.name}{free_tag}{price}")
                op = row.operator("ai.select_model", text="", icon="CHECKMARK")
                op.model_name = model.name

        box.operator("ai.test_connection", text="Test Connection", icon="VIEWZOOM")

        box = layout.box()
        box.label(text="General:", icon="PREFERENCES")
        box.prop(p, "temperature", text="Temperature")
        box.prop(p, "max_tokens", text="Max Tokens")
        box.prop(p, "auto_execute", text="Auto-execute")
        box.prop(p, "language", text="Language")

        box.operator("ai.save_config", text="💾 Save Settings", icon="FILE_TICK")


# ═══════════════════════════════════════════════════════════════
# REGISTRATION
# ═══════════════════════════════════════════════════════════════

classes = (
    AIMessage,
    AIModelItem,
    AIProps,
    AI_OT_Send,
    AI_OT_Clear,
    AI_OT_AttachImage,
    AI_OT_StartServer,
    AI_OT_StopServer,
    AI_OT_SaveConfig,
    AI_OT_TestConnection,
    AI_OT_FetchModels,
    AI_OT_SelectModel,
    AI_OT_VoiceToggle,
    AI_PT_Main,
    AI_PT_Chat,
    AI_PT_Settings,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.ai_props = bpy.props.PointerProperty(type=AIProps)

    config = load_config()
    p = bpy.context.scene.ai_props
    for key in [
        "provider",
        "server_url",
        "selected_model",
        "temperature",
        "max_tokens",
        "language",
    ]:
        if key in config:
            setattr(p, key, config[key])

    for msg_data in load_history():
        msg = p.chat_messages.add()
        msg.role = msg_data.get("role", "user")
        msg.content = msg_data.get("content", "")
        msg.timestamp = msg_data.get("timestamp", "")

    print("[AI Assistant PRO v7.0] Ready - Connects to OpenCode server")


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.ai_props


if __name__ == "__main__":
    register()
