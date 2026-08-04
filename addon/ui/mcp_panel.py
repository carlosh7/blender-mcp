"""
blender-mcp — UI Panel (Simplified)
Panel profesional con solo features ÚNICOS que Blender NO tiene.
"""
import bpy
from bpy.props import EnumProperty, IntProperty, StringProperty
from bpy.types import Panel, Operator


# ═══════════════════════════════════════════════════════════════
# OPERADORES ÚNICOS
# ═══════════════════════════════════════════════════════════════

class MCP_UL_TextTo3D(Operator):
    """Crear modelo 3D desde descripción textual"""
    bl_idname = "mcp_ultra.text_to_3d"
    bl_label = "Text to 3D"
    bl_description = "Create 3D model from natural language description"
    
    def execute(self, context):
        props = context.scene.mcp_ultra
        if not props.text_description:
            self.report({'ERROR'}, "Enter a description")
            return {'CANCELLED'}
        
        try:
            from ..ai import ai_assistant
            obj = ai_assistant.text_to_3d(props.text_description)
            if obj:
                self.report({'INFO'}, f"Created: {obj.name}")
            else:
                self.report({'ERROR'}, "Failed to create object")
        except Exception as e:
            self.report({'ERROR'}, str(e))
        return {'FINISHED'}


class MCP_UL_ImageTo3D(Operator):
    """Crear modelo 3D desde imagen"""
    bl_idname = "mcp_ultra.image_to_3d"
    bl_label = "Image to 3D"
    bl_description = "Create 3D model from reference image"
    
    def execute(self, context):
        props = context.scene.mcp_ultra
        if not props.image_path:
            self.report({'ERROR'}, "Select an image first")
            return {'CANCELLED'}
        
        try:
            from ..ai import ai_assistant
            obj = ai_assistant.image_to_3d(props.image_path)
            if obj:
                self.report({'INFO'}, f"Created: {obj.name}")
            else:
                self.report({'ERROR'}, "Failed to create object")
        except Exception as e:
            self.report({'ERROR'}, str(e))
        return {'FINISHED'}


class MCP_UL_AnalyzeScene(Operator):
    """Analizar escena con percepción"""
    bl_idname = "mcp_ultra.analyze_scene"
    bl_label = "Analyze Scene"
    bl_description = "Scan and analyze the entire scene"
    
    def execute(self, context):
        try:
            from ..perception import perception_system
            result = perception_system.analyze_scene()
            score = result["summary"]["score"]
            action = result["summary"]["action"]
            objects = result["summary"]["total_objects"]
            anomalies = result["summary"]["anomalies"]
            
            msg = f"Score: {score}/100 | Objects: {objects} | Anomalies: {anomalies}"
            self.report({'INFO'}, msg)
        except Exception as e:
            self.report({'ERROR'}, str(e))
        return {'FINISHED'}


class MCP_UL_RefineQuality(Operator):
    """Refinar calidad automáticamente"""
    bl_idname = "mcp_ultra.refine_quality"
    bl_label = "Refine Quality"
    bl_description = "Auto-improve scene quality"
    
    def execute(self, context):
        props = context.scene.mcp_ultra
        try:
            from ..perception import quality_refinement
            result = quality_refinement.refine_quality(props.target_quality)
            score = result["final_quality"]
            improvements = len(result["improvements"])
            self.report({'INFO'}, f"Quality: {score}/100 | Improvements: {improvements}")
        except Exception as e:
            self.report({'ERROR'}, str(e))
        return {'FINISHED'}


class MCP_UL_LoadReference(Operator):
    """Cargar imagen de referencia"""
    bl_idname = "mcp_ultra.load_reference"
    bl_label = "Load Reference"
    bl_description = "Load reference image for guiding creation"
    
    def execute(self, context):
        props = context.scene.mcp_ultra
        if not props.image_path:
            self.report({'ERROR'}, "Select an image path")
            return {'CANCELLED'}
        
        try:
            from ..perception import reference_system
            ref = reference_system.ReferenceManager()
            result = ref.load_reference(props.image_path)
            if isinstance(result, dict) and "error" in result:
                self.report({'ERROR'}, result["error"])
            else:
                self.report({'INFO'}, f"Reference loaded: {props.image_path}")
        except Exception as e:
            self.report({'ERROR'}, str(e))
        return {'FINISHED'}


# ═══════════════════════════════════════════════════════════════
# PANELES SIMPLIFICADOS
# ═══════════════════════════════════════════════════════════════

class MCP_UL_AIAssistantPanel(Panel):
    """Panel de asistente IA"""
    bl_label = "AI Assistant"
    bl_idname = "MCP_UL_PT_ai"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MCP"
    bl_parent_id = "MCPUltra_PT_main"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.mcp_ultra
        
        # Text to 3D
        box = layout.box()
        box.label(text="Text to 3D:", icon='OUTLINER_OB_MESH')
        box.prop(props, "text_description", text="Description")
        box.operator("mcp_ultra.text_to_3d", text="Create", icon='PLAY')
        
        # Image to 3D
        box = layout.box()
        box.label(text="Image to 3D:", icon='IMAGE_DATA')
        box.prop(props, "image_path", text="Image")
        box.operator("mcp_ultra.image_to_3d", text="Create", icon='PLAY')


class MCP_UL_PerceptionPanel(Panel):
    """Panel de percepción"""
    bl_label = "Perception"
    bl_idname = "MCP_UL_PT_perception"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MCP"
    bl_parent_id = "MCPUltra_PT_main"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.mcp_ultra
        
        # Analyze
        box = layout.box()
        box.label(text="Scene Analysis:", icon='VIEWZOOM')
        box.operator("mcp_ultra.analyze_scene", text="Analyze", icon='PLAY')
        
        # Refine
        box = layout.box()
        box.label(text="Quality Refinement:", icon='MOD_SMOOTH')
        box.prop(props, "target_quality", text="Target")
        box.operator("mcp_ultra.refine_quality", text="Refine", icon='PLAY')


class MCP_UL_ReferencesPanel(Panel):
    """Panel de referencias"""
    bl_label = "References"
    bl_idname = "MCP_UL_PT_references"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MCP"
    bl_parent_id = "MCPUltra_PT_main"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.mcp_ultra
        
        box = layout.box()
        box.label(text="Reference Images:", icon='IMAGE_DATA')
        box.prop(props, "image_path", text="Path")
        box.operator("mcp_ultra.load_reference", text="Load", icon='FILE_FOLDER')


# ═══════════════════════════════════════════════════════════════
# REGISTRO
# ═══════════════════════════════════════════════════════════════

classes = (
    MCP_UL_TextTo3D,
    MCP_UL_ImageTo3D,
    MCP_UL_AnalyzeScene,
    MCP_UL_RefineQuality,
    MCP_UL_LoadReference,
    MCP_UL_AIAssistantPanel,
    MCP_UL_PerceptionPanel,
    MCP_UL_ReferencesPanel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
