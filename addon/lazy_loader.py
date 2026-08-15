"""
blender-mcp — Lazy Loading MCP
Carga dinámica de herramientas MCP para reducir tokens.

Problema: Registrar 118 herramientas simultáneamente consume miles de tokens.
Solución: Cargar ~15 herramientas base y exponer avanzadas bajo demanda.
"""
from typing import Dict, List, Set, Callable, Any


# ═══════════════════════════════════════════════════════════════
# TOOL REGISTRY
# ═══════════════════════════════════════════════════════════════

class ToolRegistry:
    """
    Registro de herramientas MCP con carga lazy.
    
    Categorías:
    - core: Siempre cargadas (15 herramientas base)
    - modeling: BMesh, primitivas avanzadas
    - texturing: PBR, UV, materiales
    - rigging: Armature, IK/FK
    - animation: Ciclos, facial
    - characters: Personajes, sculpting
    - perception: Escaneo, validación
    - export: Formatos, LOD
    - physics: Simulación
    - ai: Text-to-3D, vision
    """
    
    CORE_TOOLS = {
        "get_scene_info",
        "get_viewport_screenshot",
        "create_object",
        "validate_object",
        "validate_scene",
        "get_spatial_visual",
        "snap_to_anchor",
        "apply_symmetry",
        "fix_normals",
        "cleanup_scene",
        "analyze_performance",
        "ping",
        "diagnose",
        "get_state",
        "create_collection",
    }
    
    CATEGORY_TOOLS = {
        "modeling": {
            "create_primitive",
            "apply_boolean",
            "subdivide_mesh",
            "bevel_edges",
            "extrude_faces",
            "inset_faces",
            "bridge_edge_loops",
            "lattice_deform",
            "create_lathe",
            "create_gear",
            "create_spring",
            "create_capsule",
            "create_pyramid",
        },
        "texturing": {
            "apply_material",
            "create_pbr_material",
            "smart_uv_unwrap",
            "project_uv",
            "bake_texture",
            "create_procedural_texture",
            "apply_normal_map",
            "apply_displacement",
        },
        "rigging": {
            "create_armature",
            "add_ik_chain",
            "add_fk_chain",
            "auto_rig",
            "weight_paint",
            "add_bone_constraints",
        },
        "animation": {
            "create_animation",
            "create_walk_cycle",
            "create_run_cycle",
            "create_idle_animation",
            "create_facial_expression",
            "lip_sync",
            "eye_tracking",
        },
        "characters": {
            "create_character",
            "create_humanoid",
            "create_quadruped",
            "create_avian",
            "create_reptile",
            "create_fantasy",
        },
        "perception": {
            "analyze_scene",
            "get_object_anchors",
            "get_model_blueprint",
            "validate_geometry",
            "get_spatial_summary",
            "quality_check",
            "detect_anomalies",
        },
        "export": {
            "export_glb",
            "export_fbx",
            "export_obj",
            "export_stl",
            "export_usd",
            "export_alembic",
            "create_lod",
        },
        "physics": {
            "add_rigid_body",
            "add_cloth",
            "add_fluid",
            "add_particles",
            "add_soft_body",
            "add_force_field",
            "add_collision",
        },
        "ai": {
            "text_to_3d",
            "image_to_3d",
            "search_assets",
            "generate_3d",
            "analyze_image",
        },
    }
    
    def __init__(self):
        self._loaded_categories: Set[str] = {"core"}
        self._all_tools = set(self.CORE_TOOLS)
        for cat, tools in self.CATEGORY_TOOLS.items():
            self._all_tools.update(tools)
    
    def get_loaded_tools(self) -> Set[str]:
        """Obtener herramientas actualmente cargadas."""
        tools = set(self.CORE_TOOLS)
        for cat in self._loaded_categories:
            if cat in self.CATEGORY_TOOLS:
                tools.update(self.CATEGORY_TOOLS[cat])
        return tools
    
    def load_category(self, category: str) -> bool:
        """
        Cargar categoría de herramientas.
        
        Args:
            category: Nombre de la categoría
        
        Returns:
            True si se cargó, False si no existe
        """
        if category not in self.CATEGORY_TOOLS:
            return False
        
        self._loaded_categories.add(category)
        return True
    
    def load_categories(self, categories: List[str]) -> Dict[str, bool]:
        """
        Cargar múltiples categorías.
        
        Args:
            categories: Lista de categorías
        
        Returns:
            Dict con resultado por categoría
        """
        return {cat: self.load_category(cat) for cat in categories}
    
    def get_tool_count(self) -> Dict[str, int]:
        """Obtener conteo de herramientas."""
        loaded = self.get_loaded_tools()
        total = len(self._all_tools)
        return {
            "loaded": len(loaded),
            "total": total,
            "categories_loaded": len(self._loaded_categories),
            "categories_total": len(self.CATEGORY_TOOLS),
        }
    
    def is_tool_available(self, tool_name: str) -> bool:
        """Verificar si una herramienta está disponible."""
        return tool_name in self.get_loaded_tools()
    
    def get_missing_tools(self) -> Set[str]:
        """Obtener herramientas no cargadas."""
        return self._all_tools - self.get_loaded_tools()
    
    def auto_load_for_task(self, task_description: str) -> List[str]:
        """
        Cargar automáticamente categorías según la tarea.
        
        Args:
            task_description: Descripción de la tarea
        
        Returns:
            Lista de categorías cargadas
        """
        task_lower = task_description.lower()
        loaded = []
        
        keyword_map = {
            "modeling": ["model", "mesh", "create", "primitive", "boolean", "extrude"],
            "texturing": ["texture", "material", "pbr", "uv", "color"],
            "rigging": ["rig", "armature", "bone", "ik", "fk"],
            "animation": ["animate", "animation", "walk", "run", "cycle"],
            "characters": ["character", "humanoid", "person", "creature"],
            "perception": ["scan", "analyze", "validate", "check"],
            "export": ["export", "fbx", "glb", "stl", "obj"],
            "physics": ["physics", "rigid", "cloth", "fluid", "particle"],
            "ai": ["ai", "text to 3d", "image to 3d", "generate"],
        }
        
        for category, keywords in keyword_map.items():
            if any(kw in task_lower for kw in keywords):
                if self.load_category(category):
                    loaded.append(category)
        
        return loaded


# ═══════════════════════════════════════════════════════════════
# INSTANCIA GLOBAL
# ═══════════════════════════════════════════════════════════════

tool_registry = ToolRegistry()


# ═══════════════════════════════════════════════════════════════
# TOOL LIST GENERATOR
# ═══════════════════════════════════════════════════════════════

def get_tool_list_for_llm() -> List[Dict[str, str]]:
    """
    Generar lista de herramientas formateada para el LLM.
    
    Returns:
        Lista de dicts con name, description, category
    """
    tools = []
    
    # Core tools
    for tool in sorted(ToolRegistry.CORE_TOOLS):
        tools.append({
            "name": tool,
            "description": f"Core tool: {tool}",
            "category": "core",
        })
    
    # Category tools
    for category in tool_registry._loaded_categories:
        if category in ToolRegistry.CATEGORY_TOOLS:
            for tool in sorted(ToolRegistry.CATEGORY_TOOLS[category]):
                tools.append({
                    "name": tool,
                    "description": f"{category.title()} tool: {tool}",
                    "category": category,
                })
    
    return tools


def get_compact_tool_list() -> str:
    """
    Generar lista compacta de herramientas.
    
    Returns:
        String con herramientas formateadas
    """
    tools = get_tool_list_for_llm()
    
    lines = [f"Available tools ({len(tools)} total):"]
    for tool in tools:
        lines.append(f"  - {tool['name']} ({tool['category']})")
    
    return "\n".join(lines)
