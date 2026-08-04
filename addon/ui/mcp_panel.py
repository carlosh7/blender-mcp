"""
blender-mcp — UI Panel
Panel de usuario profesional para blender-mcp-ultra.
Integra todos los módulos: Modeling, Texturing, Rigging, Animation, etc.
"""
import bpy
from bpy.props import EnumProperty, IntProperty, StringProperty
from bpy.types import Panel, Operator


# ═══════════════════════════════════════════════════════════════
# OPERADORES
# ═══════════════════════════════════════════════════════════════

class MCP_UL_CreatePrimitive(Operator):
    """Crear primitiva avanzada"""
    bl_idname = "mcp_ultra.create_primitive"
    bl_label = "Create Primitive"
    
    def execute(self, context):
        props = context.scene.mcp_ultra
        try:
            from ..core import mesh_engine
            obj = mesh_engine.create_advanced_primitive(props.primitive_type)
            self.report({'INFO'}, f"Created: {obj.name}")
        except Exception as e:
            self.report({'ERROR'}, str(e))
        return {'FINISHED'}


class MCP_UL_ApplyMaterial(Operator):
    """Aplicar material PBR"""
    bl_idname = "mcp_ultra.apply_material"
    bl_label = "Apply Material"
    
    def execute(self, context):
        props = context.scene.mcp_ultra
        obj = context.active_object
        if not obj:
            self.report({'ERROR'}, "No active object")
            return {'CANCELLED'}
        
        try:
            from ..core import texture_engine
            mat = texture_engine.create_pbr_material(f"Mat_{props.material_type}", props.material_type)
            obj.data.materials.append(mat)
            self.report({'INFO'}, f"Applied: {props.material_type}")
        except Exception as e:
            self.report({'ERROR'}, str(e))
        return {'FINISHED'}


class MCP_UL_CreateRig(Operator):
    """Crear esqueleto"""
    bl_idname = "mcp_ultra.create_rig"
    bl_label = "Create Rig"
    
    def execute(self, context):
        props = context.scene.mcp_ultra
        try:
            from ..core import rig_engine
            if props.rig_type == "humanoid":
                obj = rig_engine.create_humanoid_rig()
            else:
                obj = rig_engine.create_quadruped_rig()
            self.report({'INFO'}, f"Created: {obj.name}")
        except Exception as e:
            self.report({'ERROR'}, str(e))
        return {'FINISHED'}


class MCP_UL_CreateAnimation(Operator):
    """Crear animación"""
    bl_idname = "mcp_ultra.create_animation"
    bl_label = "Create Animation"
    
    def execute(self, context):
        props = context.scene.mcp_ultra
        obj = context.active_object
        if not obj:
            self.report({'ERROR'}, "No active object")
            return {'CANCELLED'}
        
        try:
            from ..core import animation_engine
            if props.animation_type == "walk":
                animation_engine.create_walk_cycle(obj)
            elif props.animation_type == "run":
                animation_engine.create_run_cycle(obj)
            elif props.animation_type == "idle":
                animation_engine.create_idle_animation(obj)
            elif props.animation_type == "jump":
                animation_engine.create_jump_animation(obj)
            elif props.animation_type == "wave":
                animation_engine.create_wave_animation(obj)
            elif props.animation_type == "spin":
                animation_engine.create_spin_animation(obj)
            self.report({'INFO'}, f"Created: {props.animation_type}")
        except Exception as e:
            self.report({'ERROR'}, str(e))
        return {'FINISHED'}


class MCP_UL_CreateCharacter(Operator):
    """Crear personaje"""
    bl_idname = "mcp_ultra.create_character"
    bl_label = "Create Character"
    
    def execute(self, context):
        props = context.scene.mcp_ultra
        try:
            from ..organic import character_gen
            parts = character_gen.create_character(props.character_type)
            self.report({'INFO'}, f"Created: {len(parts)} parts")
        except Exception as e:
            self.report({'ERROR'}, str(e))
        return {'FINISHED'}


class MCP_UL_AnalyzeScene(Operator):
    """Analizar escena"""
    bl_idname = "mcp_ultra.analyze_scene"
    bl_label = "Analyze Scene"
    
    def execute(self, context):
        try:
            from ..perception import perception_system
            result = perception_system.analyze_scene()
            score = result["summary"]["score"]
            action = result["summary"]["action"]
            self.report({'INFO'}, f"Score: {score}/100, Action: {action}")
        except Exception as e:
            self.report({'ERROR'}, str(e))
        return {'FINISHED'}


class MCP_UL_RefineQuality(Operator):
    """Refinar calidad"""
    bl_idname = "mcp_ultra.refine_quality"
    bl_label = "Refine Quality"
    
    def execute(self, context):
        props = context.scene.mcp_ultra
        try:
            from ..perception import quality_refinement
            result = quality_refinement.refine_quality(props.target_quality)
            score = result["final_quality"]
            self.report({'INFO'}, f"Quality: {score}/100")
        except Exception as e:
            self.report({'ERROR'}, str(e))
        return {'FINISHED'}


class MCP_UL_Export(Operator):
    """Exportar escena"""
    bl_idname = "mcp_ultra.export"
    bl_label = "Export"
    
    def execute(self, context):
        props = context.scene.mcp_ultra
        try:
            from ..export import export_engine
            filepath = f"/tmp/scene.{props.export_format.lower()}"
            result = export_engine.smart_export(filepath, props.export_format)
            if result.get("success"):
                self.report({'INFO'}, f"Exported: {filepath}")
            else:
                self.report({'ERROR'}, result.get("error", "Export failed"))
        except Exception as e:
            self.report({'ERROR'}, str(e))
        return {'FINISHED'}


class MCP_UL_TextTo3D(Operator):
    """Crear 3D desde texto"""
    bl_idname = "mcp_ultra.text_to_3d"
    bl_label = "Text to 3D"
    
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


# ═══════════════════════════════════════════════════════════════
# PANELES
# ═══════════════════════════════════════════════════════════════

class MCP_UL_ModelingPanel(Panel):
    """Panel de modelado"""
    bl_label = "Modeling"
    bl_idname = "MCP_UL_PT_modeling"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MCP"
    bl_parent_id = "MCPUltra_PT_main"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.mcp_ultra
        
        layout.prop(props, "primitive_type")
        layout.operator("mcp_ultra.create_primitive", icon='MESH_CUBE')


class MCP_UL_TexturingPanel(Panel):
    """Panel de texturizado"""
    bl_label = "Texturing"
    bl_idname = "MCP_UL_PT_texturing"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MCP"
    bl_parent_id = "MCPUltra_PT_main"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.mcp_ultra
        
        layout.prop(props, "material_type")
        layout.operator("mcp_ultra.apply_material", icon='MATERIAL')


class MCP_UL_RiggingPanel(Panel):
    """Panel de rigging"""
    bl_label = "Rigging"
    bl_idname = "MCP_UL_PT_rigging"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MCP"
    bl_parent_id = "MCPUltra_PT_main"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.mcp_ultra
        
        layout.prop(props, "rig_type")
        layout.operator("mcp_ultra.create_rig", icon='ARMATURE_DATA')


class MCP_UL_AnimationPanel(Panel):
    """Panel de animación"""
    bl_label = "Animation"
    bl_idname = "MCP_UL_PT_animation"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MCP"
    bl_parent_id = "MCPUltra_PT_main"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.mcp_ultra
        
        layout.prop(props, "animation_type")
        layout.operator("mcp_ultra.create_animation", icon='PLAY')


class MCP_UL_CharacterPanel(Panel):
    """Panel de personajes"""
    bl_label = "Characters"
    bl_idname = "MCP_UL_PT_character"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MCP"
    bl_parent_id = "MCPUltra_PT_main"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.mcp_ultra
        
        layout.prop(props, "character_type")
        layout.operator("mcp_ultra.create_character", icon='USER')


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
        
        layout.operator("mcp_ultra.analyze_scene", icon='VIEWZOOM')
        layout.operator("mcp_ultra.refine_quality", icon='MOD_SMOOTH')
        layout.prop(props, "target_quality")


class MCP_UL_ExportPanel(Panel):
    """Panel de exportación"""
    bl_label = "Export"
    bl_idname = "MCP_UL_PT_export"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MCP"
    bl_parent_id = "MCPUltra_PT_main"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.mcp_ultra
        
        layout.prop(props, "export_format")
        layout.operator("mcp_ultra.export", icon='EXPORT')


class MCP_UL_TextTo3DPanel(Panel):
    """Panel de Text to 3D"""
    bl_label = "Text to 3D"
    bl_idname = "MCP_UL_PT_text_to_3d"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MCP"
    bl_parent_id = "MCPUltra_PT_main"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.mcp_ultra
        
        layout.prop(props, "text_description")
        layout.operator("mcp_ultra.text_to_3d", icon='OUTLINER_OB_MESH')


# ═══════════════════════════════════════════════════════════════
# REGISTRO (solo operadores y paneles, NO propiedades)
# ═══════════════════════════════════════════════════════════════

classes = (
    MCP_UL_CreatePrimitive,
    MCP_UL_ApplyMaterial,
    MCP_UL_CreateRig,
    MCP_UL_CreateAnimation,
    MCP_UL_CreateCharacter,
    MCP_UL_AnalyzeScene,
    MCP_UL_RefineQuality,
    MCP_UL_Export,
    MCP_UL_TextTo3D,
    MCP_UL_ModelingPanel,
    MCP_UL_TexturingPanel,
    MCP_UL_RiggingPanel,
    MCP_UL_AnimationPanel,
    MCP_UL_CharacterPanel,
    MCP_UL_PerceptionPanel,
    MCP_UL_ExportPanel,
    MCP_UL_TextTo3DPanel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
