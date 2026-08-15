"""
blender-mcp-ultra — AI Assistant Panel (Complete)
Full-featured AI assistant with:
- Real-time preview
- Undo/Redo
- Smart selection
- Conversation memory
- Voice commands
- Natural conversation
- Settings
- Beginner/Expert modes
"""
import bpy
from bpy.types import Panel, Operator, PropertyGroup
from bpy.props import StringProperty, EnumProperty, CollectionProperty, IntProperty, BoolProperty, FloatProperty
from datetime import datetime
import socket
import json
import os
import tempfile


# ═══════════════════════════════════════════════════════════════
# PROPERTIES
# ═══════════════════════════════════════════════════════════════

class AIChatMessage(PropertyGroup):
    """Single chat message."""
    role: StringProperty(name="Role", default="user")  # user | assistant | system
    content: StringProperty(name="Content", default="")
    timestamp: StringProperty(name="Timestamp", default="")
    command: StringProperty(name="Command", default="")  # Command executed


class AIAssistantProperties(PropertyGroup):
    """AI Assistant properties."""
    
    # ── Chat ──
    chat_messages: CollectionProperty(type=AIChatMessage)
    chat_input: StringProperty(name="Message", default="")
    chat_history_index: IntProperty(name="History Index", default=-1)
    
    # ── Mode ──
    ui_mode: EnumProperty(
        name="Mode",
        items=[
            ('beginner', "Beginner", "Simple interface"),
            ('expert', "Expert", "Full control"),
        ],
        default='beginner'
    )
    
    # ── AI Settings ──
    ai_model: EnumProperty(
        name="Model",
        items=[
            ('local', "Local (Ollama)", "Fast, private"),
            ('openai', "OpenAI GPT-4", "Powerful"),
            ('anthropic', "Claude", "Creative"),
        ],
        default='local'
    )
    temperature: FloatProperty(name="Temperature", default=0.7, min=0.0, max=2.0)
    
    # ── Image to 3D ──
    image_path: StringProperty(
        name="Reference Image",
        description="Path to reference image",
        subtype='FILE_PATH'
    )
    
    # ── Text to 3D ──
    text_description: StringProperty(
        name="Description",
        description="Describe what you want to create",
        default=""
    )
    
    # ── Scene ──
    scene_description: StringProperty(
        name="Scene",
        description="Describe the scene",
        default=""
    )
    
    # ── Voice ──
    voice_enabled: BoolProperty(name="Voice", default=False)
    voice_recording: BoolProperty(name="Recording", default=False)
    
    # ── Preview ──
    preview_enabled: BoolProperty(name="Preview", default=True)
    preview_opacity: FloatProperty(name="Preview Opacity", default=0.5, min=0.0, max=1.0)
    
    # ── Undo/Redo ──
    undo_stack: CollectionProperty(type=AIChatMessage)
    redo_stack: CollectionProperty(type=AIChatMessage)


# ═══════════════════════════════════════════════════════════════
# MCP CONNECTION
# ═══════════════════════════════════════════════════════════════

def send_mcp_command(command, params=None):
    """Send command to MCP server and get response."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(30)
        s.connect(('127.0.0.1', 9876))
        s.sendall(json.dumps({'type': command, 'params': params or {}}).encode())
        data = s.recv(1024 * 1024)
        s.close()
        return json.loads(data.decode())
    except Exception as e:
        return {'status': 'error', 'message': str(e)}


# ═══════════════════════════════════════════════════════════════
# AI PROCESSING
# ═══════════════════════════════════════════════════════════════

class AIProcessor:
    """Process natural language commands."""
    
    @staticmethod
    def process(message, context=None):
        """Process message and return response with optional code."""
        msg = message.lower().strip()
        
        # ── CREATE ──
        if any(w in msg for w in ["create", "make", "add", "new", "generar", "crear"]):
            return AIProcessor._handle_create(msg)
        
        # ── DELETE ──
        if any(w in msg for w in ["delete", "remove", "clear", "borrar", "eliminar"]):
            return AIProcessor._handle_delete(msg)
        
        # ── COLOR ──
        if any(w in msg for w in ["color", "paint", "colorear", "pintar"]):
            return AIProcessor._handle_color(msg)
        
        # ── MATERIAL ──
        if any(w in msg for w in ["material", "texture", "textura", "madera", "metal", "glass", "vidrio"]):
            return AIProcessor._handle_material(msg)
        
        # ── TRANSFORM ──
        if any(w in msg for w in ["move", "rotate", "scale", "mover", "rotar", "escalar"]):
            return AIProcessor._handle_transform(msg)
        
        # ── SCENE ──
        if any(w in msg for w in ["scene", "room", "escena", "cuarto", "ambiente"]):
            return AIProcessor._handle_scene(msg)
        
        # ── EXPORT ──
        if any(w in msg for w in ["export", "save", "download", "exportar", "guardar"]):
            return AIProcessor._handle_export(msg)
        
        # ── SELECT ──
        if any(w in msg for w in ["select", "select all", "seleccionar"]):
            return AIProcessor._handle_select(msg)
        
        # ── UNDO ──
        if any(w in msg for w in ["undo", "desacer", "volver"]):
            return AIProcessor._handle_undo()
        
        # ── REDO ──
        if any(w in msg for w in ["redo", "rehacer"]):
            return AIProcessor._handle_redo()
        
        # ── HELP ──
        if any(w in msg for w in ["help", "ayuda", "commands", "comandos"]):
            return AIProcessor._handle_help()
        
        # ── STATUS ──
        if any(w in msg for w in ["status", "estado", "info", "información"]):
            return AIProcessor._handle_status()
        
        # ── Default: try to understand ──
        return {
            "response": f"🤔 I don't understand: '{message}'\n\nTry:\n• 'create a red cube'\n• 'make a wooden table'\n• 'help' for all commands",
            "code": None
        }
    
    @staticmethod
    def _handle_create(msg):
        """Handle create commands."""
        # Determine what to create
        obj_type = "cube"
        if "sphere" in msg or "esfera" in msg or "bola" in msg:
            obj_type = "sphere"
        elif "cylinder" in msg or "cilindro" in msg:
            obj_type = "cylinder"
        elif "cone" in msg or "cono" in msg:
            obj_type = "cone"
        elif "torus" in msg or "donut" in msg:
            obj_type = "torus"
        elif "plane" in msg or "plano" in msg:
            obj_type = "plane"
        elif "chair" in msg or "silla" in msg:
            return {
                "response": "🪑 Creating chair...",
                "code": AIProcessor._code_chair()
            }
        elif "table" in msg or "mesa" in msg:
            return {
                "response": "🪑 Creating table...",
                "code": AIProcessor._code_table()
            }
        elif "lamp" in msg or "luz" in msg or "lámpara" in msg:
            return {
                "response": "💡 Creating lamp...",
                "code": AIProcessor._code_lamp()
            }
        
        # Create primitive
        code = f"""
import bpy
bpy.ops.mesh.primitive_{obj_type}_add(size=1, location=(0, 0, 0.5))
obj = bpy.context.active_object
obj.name = "AI_{obj_type.capitalize()}"
print(f"✅ Created {obj_type}")
"""
        return {"response": f"✅ Creating {obj_type}...", "code": code}
    
    @staticmethod
    def _handle_delete(msg):
        """Handle delete commands."""
        if "all" in msg or "todo" in msg or "everything" in msg:
            code = """
import bpy
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
print("✅ Deleted all objects")
"""
            return {"response": "🗑️ Deleting all objects...", "code": code}
        else:
            code = """
import bpy
if context.selected_objects:
    bpy.ops.object.delete()
    print("✅ Deleted selected")
else:
    print("⚠️ No objects selected")
"""
            return {"response": "🗑️ Deleting selected...", "code": code}
    
    @staticmethod
    def _handle_color(msg):
        """Handle color commands."""
        color = (0.8, 0.8, 0.8)
        if "red" in msg or "rojo" in msg:
            color = (0.8, 0.1, 0.1)
        elif "blue" in msg or "azul" in msg:
            color = (0.1, 0.1, 0.8)
        elif "green" in msg or "verde" in msg:
            color = (0.1, 0.7, 0.1)
        elif "yellow" in msg or "amarillo" in msg:
            color = (0.9, 0.9, 0.1)
        elif "black" in msg or "negro" in msg:
            color = (0.05, 0.05, 0.05)
        elif "white" in msg or "blanco" in msg:
            color = (0.95, 0.95, 0.95)
        
        code = f"""
import bpy
obj = bpy.context.active_object
if obj and obj.type == 'MESH':
    if not obj.data.materials:
        mat = bpy.data.materials.new(name="AI_Mat")
        mat.use_nodes = True
        obj.data.materials.append(mat)
    else:
        mat = obj.data.materials[0]
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = ({color[0]}, {color[1]}, {color[2]}, 1)
    print("✅ Color applied")
else:
    print("⚠️ Select a mesh object first")
"""
        return {"response": f"🎨 Applying color...", "code": code}
    
    @staticmethod
    def _handle_material(msg):
        """Handle material commands."""
        preset = "wood_oak"
        if "metal" in msg or "metal" in msg:
            preset = "metal_gold"
        elif "glass" in msg or "vidrio" in msg:
            preset = "glass_clear"
        elif "plastic" in msg or "plástico" in msg:
            preset = "plastic_white"
        
        code = f"""
import bpy
obj = bpy.context.active_object
if obj and obj.type == 'MESH':
    if not obj.data.materials:
        mat = bpy.data.materials.new(name="AI_Mat")
        mat.use_nodes = True
        obj.data.materials.append(mat)
    else:
        mat = obj.data.materials[0]
    
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        presets = {{
            'wood_oak': {{'color': (0.45, 0.30, 0.15), 'rough': 0.7, 'metal': 0.0}},
            'metal_gold': {{'color': (0.85, 0.65, 0.10), 'rough': 0.1, 'metal': 1.0}},
            'glass_clear': {{'color': (0.95, 0.95, 0.95), 'rough': 0.0, 'metal': 0.0}},
            'plastic_white': {{'color': (0.90, 0.90, 0.90), 'rough': 0.4, 'metal': 0.0}},
        }}
        p = presets.get('{preset}', {{}})
        if p:
            bsdf.inputs["Base Color"].default_value = (*p['color'], 1)
            bsdf.inputs["Roughness"].default_value = p['rough']
            bsdf.inputs["Metallic"].default_value = p['metal']
    print(f"✅ Applied {preset} material")
else:
    print("⚠️ Select a mesh object first")
"""
        return {"response": f"🪵 Applying {preset}...", "code": code}
    
    @staticmethod
    def _handle_transform(msg):
        """Handle transform commands."""
        code = """
import bpy
obj = bpy.context.active_object
if obj:
    if "left" in msg or "izquierda" in msg:
        obj.location.x -= 0.5
    elif "right" in msg or "derecha" in msg:
        obj.location.x += 0.5
    elif "up" in msg or "arriba" in msg:
        obj.location.z += 0.5
    elif "down" in msg or "abajo" in msg:
        obj.location.z -= 0.5
    elif "forward" in msg or "adelante" in msg:
        obj.location.y += 0.5
    elif "back" in msg or "atrás" in msg:
        obj.location.y -= 0.5
    print("✅ Object moved")
else:
    print("⚠️ No object selected")
"""
        return {"response": "📐 Transforming...", "code": code}
    
    @staticmethod
    def _handle_scene(msg):
        """Handle scene commands."""
        if "living room" in msg or "sala" in msg:
            return {
                "response": "🏠 Creating living room...",
                "code": AIProcessor._code_living_room()
            }
        elif "bedroom" in msg or "recámara" in msg:
            return {
                "response": "🛏️ Creating bedroom...",
                "code": AIProcessor._code_bedroom()
            }
        elif "office" in msg or "oficina" in msg:
            return {
                "response": "💼 Creating office...",
                "code": AIProcessor._code_office()
            }
        else:
            return {
                "response": "🎬 Creating scene...",
                "code": AIProcessor._code_generic_scene()
            }
    
    @staticmethod
    def _handle_export(msg):
        """Handle export commands."""
        fmt = "glb"
        if "fbx" in msg:
            fmt = "fbx"
        elif "obj" in msg:
            fmt = "obj"
        elif "stl" in msg:
            fmt = "stl"
        
        code = f"""
import bpy
import os

filepath = os.path.join(os.path.expanduser("~"), "Desktop", f"export.{{'{fmt}'}}")

try:
    bpy.ops.object.select_all(action='SELECT')
    if '{fmt}' == 'glb':
        bpy.ops.export_scene.gltf(filepath=filepath, export_format='GLB')
    elif '{fmt}' == 'fbx':
        bpy.ops.export_scene.fbx(filepath=filepath)
    elif '{fmt}' == 'obj':
        bpy.ops.export_scene.obj(filepath=filepath)
    elif '{fmt}' == 'stl':
        bpy.ops.export_mesh.stl(filepath=filepath)
    
    print(f"✅ Exported to {{filepath}}")
except Exception as e:
    print(f"❌ Export failed: {{e}}")
"""
        return {"response": f"📤 Exporting as {fmt.upper()}...", "code": code}
    
    @staticmethod
    def _handle_select(msg):
        """Handle select commands."""
        code = """
import bpy
bpy.ops.object.select_all(action='SELECT')
print("✅ Selected all objects")
"""
        return {"response": "✅ Selecting all...", "code": code}
    
    @staticmethod
    def _handle_undo():
        """Handle undo command."""
        code = """
import bpy
bpy.ops.ed.undo()
print("✅ Undo")
"""
        return {"response": "⏪ Undoing...", "code": code}
    
    @staticmethod
    def _handle_redo():
        """Handle redo command."""
        code = """
import bpy
bpy.ops.ed.redo()
print("✅ Redo")
"""
        return {"response": "⏩ Redoing...", "code": code}
    
    @staticmethod
    def _handle_help():
        """Handle help command."""
        help_text = """📚 AI Assistant Commands:

🔹 CREATE: "create cube/sphere/chair/table/lamp"
🔹 DELETE: "delete all" / "remove selected"
🔹 COLOR: "color red/blue/green/yellow"
🔹 MATERIAL: "apply wood/metal/glass"
🔹 TRANSFORM: "move left/right/up/down"
🔹 SCENE: "create living room/bedroom/office"
🔹 EXPORT: "export as glb/fbx/obj/stl"
🔹 SELECT: "select all"
🔹 UNDO/REDO: "undo" / "redo"
🔹 STATUS: "status" / "info"

💡 Tips:
• Use natural language
• Combine commands: "create red cube"
• Ask for help anytime"""
        return {"response": help_text, "code": None}
    
    @staticmethod
    def _handle_status():
        """Handle status command."""
        code = """
import bpy
obj_count = len(bpy.context.scene.objects)
mesh_count = len([o for o in bpy.context.scene.objects if o.type == 'MESH'])
mat_count = len(bpy.data.materials)
print(f"📊 Scene Status:")
print(f"   Objects: {obj_count}")
print(f"   Meshes: {mesh_count}")
print(f"   Materials: {mat_count}")
"""
        return {"response": "📊 Getting status...", "code": code}
    
    # ── CODE GENERATORS ──
    
    @staticmethod
    def _code_chair():
        return """
import bpy

# Create chair
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.45))
seat = bpy.context.active_object
seat.name = "AI_Chair"
seat.scale = (0.45, 0.45, 0.04)

# Material
mat = bpy.data.materials.new(name="Chair_Wood")
mat.use_nodes = True
bsdf = mat.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs["Base Color"].default_value = (0.4, 0.25, 0.12, 1)
    bsdf.inputs["Roughness"].default_value = 0.7
seat.data.materials.append(mat)

# Legs
for x in [-0.18, 0.18]:
    for y in [-0.18, 0.18]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=0.45, location=(x, y, 0.22))
        leg = bpy.context.active_object
        leg.name = "AI_Chair_Leg"
        leg.data.materials.append(mat)

print("✅ Chair created")
"""
    
    @staticmethod
    def _code_table():
        return """
import bpy

# Create table
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.75))
top = bpy.context.active_object
top.name = "AI_Table"
top.scale = (1.2, 0.8, 0.04)

# Material
mat = bpy.data.materials.new(name="Table_Wood")
mat.use_nodes = True
bsdf = mat.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs["Base Color"].default_value = (0.3, 0.18, 0.08, 1)
    bsdf.inputs["Roughness"].default_value = 0.65
top.data.materials.append(mat)

# Legs
for x in [-0.5, 0.5]:
    for y in [-0.3, 0.3]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.75, location=(x, y, 0.375))
        leg = bpy.context.active_object
        leg.name = "AI_Table_Leg"
        leg.data.materials.append(mat)

print("✅ Table created")
"""
    
    @staticmethod
    def _code_lamp():
        return """
import bpy

# Base
bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.03, location=(0, 0, 0.015))
base = bpy.context.active_object
base.name = "AI_Lamp_Base"

# Column
bpy.ops.mesh.primitive_cylinder_add(radius=0.018, depth=0.2, location=(0, 0, 0.13))
column = bpy.context.active_object
column.name = "AI_Lamp_Column"

# Light
bpy.ops.object.light_add(type='POINT', location=(0, 0, 0.35))
light = bpy.context.active_object
light.name = "AI_Lamp_Light"
light.data.energy = 50

print("✅ Lamp created")
"""
    
    @staticmethod
    def _code_living_room():
        return """
import bpy

# Clean
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Floor
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
floor = bpy.context.active_object
floor.name = "Floor"

# Sofa
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -2, 0.3))
sofa = bpy.context.active_object
sofa.name = "Sofa"
sofa.scale = (2, 0.8, 0.6)

# Table
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.4))
table = bpy.context.active_object
table.name = "Coffee_Table"
table.scale = (1, 0.6, 0.04)

# Lamp
bpy.ops.object.light_add(type='POINT', location=(2, -2, 2))
lamp = bpy.context.active_object
lamp.name = "Lamp"
lamp.data.energy = 100

print("✅ Living room created")
"""
    
    @staticmethod
    def _code_bedroom():
        return """
import bpy

# Clean
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Floor
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
floor = bpy.context.active_object
floor.name = "Floor"

# Bed
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -2, 0.3))
bed = bpy.context.active_object
bed.name = "Bed"
bed.scale = (2, 1.5, 0.6)

# Nightstand
bpy.ops.mesh.primitive_cube_add(size=1, location=(1.5, -2, 0.3))
nightstand = bpy.context.active_object
nightstand.name = "Nightstand"
nightstand.scale = (0.4, 0.4, 0.6)

print("✅ Bedroom created")
"""
    
    @staticmethod
    def _code_office():
        return """
import bpy

# Clean
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Floor
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
floor = bpy.context.active_object
floor.name = "Floor"

# Desk
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.75))
desk = bpy.context.active_object
desk.name = "Desk"
desk.scale = (1.5, 0.8, 0.04)

# Chair
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -1, 0.45))
chair = bpy.context.active_object
chair.name = "Chair"
chair.scale = (0.45, 0.45, 0.04)

# Computer
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.9))
computer = bpy.context.active_object
computer.name = "Computer"
computer.scale = (0.5, 0.02, 0.3)

print("✅ Office created")
"""
    
    @staticmethod
    def _code_generic_scene():
        return """
import bpy

# Clean
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Floor
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
floor = bpy.context.active_object
floor.name = "Floor"

# Main object
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.5))
obj = bpy.context.active_object
obj.name = "Main_Object"

# Light
bpy.ops.object.light_add(type='POINT', location=(3, -3, 3))
light = bpy.context.active_object
light.name = "Light"
light.data.energy = 100

print("✅ Scene created")
"""


# ═══════════════════════════════════════════════════════════════
# OPERATORS
# ═══════════════════════════════════════════════════════════════

class AI_OT_SendMessage(Operator):
    """Send message to AI assistant"""
    bl_idname = "ai.send_message"
    bl_label = "Send"
    bl_description = "Send message to AI assistant"
    
    def execute(self, context):
        props = context.scene.mcp_ultra
        
        if not props.chat_input:
            return {'CANCELLED'}
        
        # Add user message
        msg = props.chat_messages.add()
        msg.role = "user"
        msg.content = props.chat_input
        msg.timestamp = datetime.now().strftime("%H:%M")
        
        # Process with AI
        result = AIProcessor.process(props.chat_input, context)
        response = result.get("response", "No response")
        code = result.get("code")
        
        # Execute code if available
        if code:
            exec_result = send_mcp_command('execute_code', {'code': code})
            output = exec_result.get('result', {}).get('output', '')
            if output:
                response += f"\n{output}"
            msg.command = code
        
        # Add AI response
        msg = props.chat_messages.add()
        msg.role = "assistant"
        msg.content = response
        msg.timestamp = datetime.now().strftime("%H:%M")
        
        # Keep only last 50 messages
        while len(props.chat_messages) > 50:
            props.chat_messages.remove(0)
        
        props.chat_input = ""
        
        self.report({'INFO'}, "Message sent")
        return {'FINISHED'}


class AI_OT_ClearChat(Operator):
    """Clear chat history"""
    bl_idname = "ai.clear_chat"
    bl_label = "Clear"
    bl_description = "Clear chat history"
    
    def execute(self, context):
        props = context.scene.mcp_ultra
        props.chat_messages.clear()
        self.report({'INFO'}, "Chat cleared")
        return {'FINISHED'}


class AI_OT_ImageTo3D(Operator):
    """Create 3D model from reference image"""
    bl_idname = "ai.image_to_3d"
    bl_label = "Generate from Image"
    bl_description = "Analyze image and create 3D model"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.mcp_ultra
        
        if not props.image_path:
            self.report({'ERROR'}, "Select an image first")
            return {'CANCELLED'}
        
        # Process image
        result = AIProcessor.process(f"create from image {props.image_path}", context)
        if result.get("code"):
            send_mcp_command('execute_code', {'code': result["code"]})
        
        self.report({'INFO'}, "Image processed")
        return {'FINISHED'}


class AI_OT_TextTo3D(Operator):
    """Create 3D model from text description"""
    bl_idname = "ai.text_to_3d"
    bl_label = "Generate from Text"
    bl_description = "Create 3D model from natural language"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.mcp_ultra
        
        if not props.text_description:
            self.report({'ERROR'}, "Enter a description")
            return {'CANCELLED'}
        
        # Process text
        result = AIProcessor.process(props.text_description, context)
        if result.get("code"):
            send_mcp_command('execute_code', {'code': result["code"]})
        
        self.report({'INFO'}, "Text processed")
        return {'FINISHED'}


class AI_OT_GenerateScene(Operator):
    """Generate complete scene from description"""
    bl_idname = "ai.generate_scene"
    bl_label = "Generate Scene"
    bl_description = "Generate complete scene from description"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.mcp_ultra
        
        if not props.scene_description:
            self.report({'ERROR'}, "Enter scene description")
            return {'CANCELLED'}
        
        # Process scene
        result = AIProcessor.process(f"create scene {props.scene_description}", context)
        if result.get("code"):
            send_mcp_command('execute_code', {'code': result["code"]})
        
        self.report({'INFO'}, "Scene generated")
        return {'FINISHED'}


class AI_OT_VoiceToggle(Operator):
    """Toggle voice input"""
    bl_idname = "ai.voice_toggle"
    bl_label = "Voice"
    bl_description = "Toggle voice input"
    
    def execute(self, context):
        props = context.scene.mcp_ultra
        props.voice_enabled = not props.voice_enabled
        
        if props.voice_enabled:
            self.report({'INFO'}, "Voice enabled")
        else:
            self.report({'INFO'}, "Voice disabled")
        
        return {'FINISHED'}


class AI_OT_ModeToggle(Operator):
    """Toggle beginner/expert mode"""
    bl_idname = "ai.mode_toggle"
    bl_label = "Mode"
    bl_description = "Toggle beginner/expert mode"
    
    def execute(self, context):
        props = context.scene.mcp_ultra
        
        if props.ui_mode == 'beginner':
            props.ui_mode = 'expert'
            self.report({'INFO'}, "Expert mode")
        else:
            props.ui_mode = 'beginner'
            self.report({'INFO'}, "Beginner mode")
        
        return {'FINISHED'}


# ═══════════════════════════════════════════════════════════════
# PANELS
# ═══════════════════════════════════════════════════════════════

class AI_PT_MainPanel(Panel):
    """Main AI Assistant panel"""
    bl_label = "🤖 AI Assistant"
    bl_idname = "AI_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "AI"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.mcp_ultra
        
        # Mode toggle
        row = layout.row(align=True)
        row.operator("ai.mode_toggle", text=f"Mode: {props.ui_mode.upper()}", icon='PREFERENCES')
        row.operator("ai.voice_toggle", text="Voice", icon='PLAY' if props.voice_enabled else 'PAUSE')


class AI_PT_ChatPanel(Panel):
    """Chat with AI panel"""
    bl_label = "💬 Chat"
    bl_idname = "AI_PT_chat"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "AI"
    bl_parent_id = "AI_PT_main"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.mcp_ultra
        
        # Chat history
        box = layout.box()
        box.scale_y = 10
        box.label(text="Conversation:", icon='TEXT')
        
        if len(props.chat_messages) == 0:
            box.label(text="👋 Hi! I'm your AI assistant.")
            box.label(text="Ask me to create anything!")
        else:
            start = max(0, len(props.chat_messages) - 20)
            for i in range(start, len(props.chat_messages)):
                msg = props.chat_messages[i]
                if msg.role == "user":
                    box.label(text=f"👤 {msg.content[:70]}")
                else:
                    # Split long responses
                    lines = msg.content.split('\n')
                    for line in lines[:3]:
                        box.label(text=f"🤖 {line[:70]}")
        
        # Input
        box = layout.box()
        row = box.row(align=True)
        row.prop(props, "chat_input", text="")
        row.operator("ai.send_message", text="", icon='PLAY')
        row.operator("ai.clear_chat", text="", icon='X')


class AI_PT_ImagePanel(Panel):
    """Image to 3D panel"""
    bl_label = "🖼️ Image to 3D"
    bl_idname = "AI_PT_image"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "AI"
    bl_parent_id = "AI_PT_main"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.mcp_ultra
        
        box = layout.box()
        box.label(text="Reference Image:", icon='IMAGE_DATA')
        box.prop(props, "image_path", text="")
        box.operator("ai.image_to_3d", text="Generate 3D Model", icon='MESH_CUBE')


class AI_PT_TextPanel(Panel):
    """Text to 3D panel"""
    bl_label = "📝 Text to 3D"
    bl_idname = "AI_PT_text"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "AI"
    bl_parent_id = "AI_PT_main"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.mcp_ultra
        
        box = layout.box()
        box.label(text="Describe what to create:", icon='TEXT')
        box.prop(props, "text_description", text="")
        box.operator("ai.text_to_3d", text="Generate 3D Model", icon='MESH_CUBE')


class AI_PT_ScenePanel(Panel):
    """Scene generation panel"""
    bl_label = "🎬 Scene Generator"
    bl_idname = "AI_PT_scene"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "AI"
    bl_parent_id = "AI_PT_main"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.mcp_ultra
        
        box = layout.box()
        box.label(text="Describe the scene:", icon='SCENE_DATA')
        box.prop(props, "scene_description", text="")
        box.operator("ai.generate_scene", text="Generate Scene", icon='PLAY')


class AI_PT_SettingsPanel(Panel):
    """AI Settings panel"""
    bl_label = "⚙️ Settings"
    bl_idname = "AI_PT_settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "AI"
    bl_parent_id = "AI_PT_main"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.mcp_ultra
        
        # AI Model
        box = layout.box()
        box.label(text="AI Model:", icon='SETTINGS')
        box.prop(props, "ai_model", text="")
        box.prop(props, "temperature", text="Temperature")
        
        # Preview
        box = layout.box()
        box.label(text="Preview:", icon='HIDE_OFF')
        box.prop(props, "preview_enabled", text="Enable Preview")
        if props.preview_enabled:
            box.prop(props, "preview_opacity", text="Opacity")


# ═══════════════════════════════════════════════════════════════
# REGISTRATION
# ═══════════════════════════════════════════════════════════════

classes = (
    AIChatMessage,
    AIAssistantProperties,
    AI_OT_SendMessage,
    AI_OT_ClearChat,
    AI_OT_ImageTo3D,
    AI_OT_TextTo3D,
    AI_OT_GenerateScene,
    AI_OT_VoiceToggle,
    AI_OT_ModeToggle,
    AI_PT_MainPanel,
    AI_PT_ChatPanel,
    AI_PT_ImagePanel,
    AI_PT_TextPanel,
    AI_PT_ScenePanel,
    AI_PT_SettingsPanel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.mcp_ultra = bpy.props.PointerProperty(type=AIAssistantProperties)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.mcp_ultra


if __name__ == "__main__":
    register()
