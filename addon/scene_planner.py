"""
blender-mcp — Scene Planner
Planificación de escenas: dependencias, orden, layout.

Regla de oro: SIEMPRE planificar ANTES de crear.
"""
import json
from datetime import datetime


# ═══════════════════════════════════════════════════════════════
# PLAN DE ESCENA
# ═══════════════════════════════════════════════════════════════

_scene_plan = {
    "name": "untitled",
    "description": "",
    "objects": [],
    "layout": {},
    "dependencies": {},
    "execution_order": [],
    "status": "draft",
    "created_at": None,
    "completed_at": None,
}


def create_plan(name, description="", objects=None):
    """
    Crear un plan de escena.
    
    Args:
        name: Nombre de la escena
        description: Descripción de la escena
        objects: Lista de objetos a crear (opcional)
    
    Returns:
        dict con el plan creado
    """
    _scene_plan["name"] = name
    _scene_plan["description"] = description
    _scene_plan["objects"] = objects or []
    _scene_plan["status"] = "planned"
    _scene_plan["created_at"] = datetime.now().isoformat()
    _scene_plan["completed_at"] = None
    
    # Calcular orden de ejecución
    _calculate_execution_order()
    
    return _scene_plan.copy()


def add_object_to_plan(object_type, position, parent=None, 
                       anchor=None, collection=None, material=None):
    """
    Agregar un objeto al plan.
    
    Args:
        object_type: Tipo de objeto (chair, table, cup, etc.)
        position: Posición (x, y, z)
        parent: Objeto padre (opcional)
        anchor: Punto de conexión (opcional)
        collection: Nombre de la colección (opcional)
        material: Material personalizado (opcional)
    
    Returns:
        dict con el objeto agregado
    """
    obj_entry = {
        "type": object_type,
        "position": position,
        "parent": parent,
        "anchor": anchor,
        "collection": collection or object_type.capitalize(),
        "material": material,
        "status": "pending",
    }
    
    _scene_plan["objects"].append(obj_entry)
    
    # Actualizar dependencias
    if parent:
        _scene_plan["dependencies"][object_type] = parent
    
    # Recalcular orden
    _calculate_execution_order()
    
    return obj_entry


def _calculate_execution_order():
    """
    Calcular el orden de ejecución basado en dependencias.
    
    - Objetos sin padre se crean primero
    - Objetos con padre se crean después del padre
    - Se respeta el orden topológico
    """
    objects = _scene_plan["objects"]
    dependencies = _scene_plan["dependencies"]
    
    # Separar raíces y dependientes
    roots = [obj for obj in objects if not obj.get("parent")]
    dependent = [obj for obj in objects if obj.get("parent")]
    
    # Ordenar dependientes por profundidad de dependencia
    order = roots.copy()
    
    def get_depth(obj_type, visited=None):
        if visited is None:
            visited = set()
        if obj_type in visited:
            return 0
        visited.add(obj_type)
        
        parent = dependencies.get(obj_type)
        if not parent:
            return 0
        return 1 + get_depth(parent, visited)
    
    # Agregar dependientes ordenados por profundidad
    dependent.sort(key=lambda obj: get_depth(obj["type"]))
    order.extend(dependent)
    
    _scene_plan["execution_order"] = order


def get_plan():
    """Obtener el plan actual."""
    return _scene_plan.copy()


def print_plan():
    """Imprimir el plan de escena."""
    print("\n" + "="*60)
    print(f"PLAN DE ESCENA: {_scene_plan['name']}")
    print("="*60)
    print(f"Descripción: {_scene_plan['description'] or 'N/A'}")
    print(f"Estado: {_scene_plan['status']}")
    print(f"Objetos: {len(_scene_plan['objects'])}")
    
    print("\n📋 Orden de ejecución:")
    for i, obj in enumerate(_scene_plan["execution_order"], 1):
        parent_info = f" → padre: {obj['parent']}" if obj.get("parent") else ""
        print(f"  {i}. {obj['type']} en {obj['position']}{parent_info}")
    
    if _scene_plan["dependencies"]:
        print("\n🔗 Dependencias:")
        for child, parent in _scene_plan["dependencies"].items():
            print(f"  {child} depende de {parent}")
    
    print("="*60)


# ═══════════════════════════════════════════════════════════════
# EJECUCIÓN DEL PLAN
# ═══════════════════════════════════════════════════════════════

def execute_plan(plan=None):
    """
    Ejecutar el plan de escena.
    
    Args:
        plan: Plan a ejecutar (opcional, usa el actual)
    
    Returns:
        dict con resultados de la ejecución
    """
    from . import creation_rules, state_manager, validator
    
    if plan:
        _scene_plan.update(plan)
    
    _scene_plan["status"] = "executing"
    results = {"success": [], "failed": []}
    
    print(f"\n🚀 Ejecutando plan: {_scene_plan['name']}")
    print(f"   Objetos a crear: {len(_scene_plan['execution_order'])}")
    
    for i, obj in enumerate(_scene_plan["execution_order"], 1):
        obj_type = obj["type"]
        position = obj["position"]
        collection = obj.get("collection")
        material = obj.get("material")
        
        print(f"\n   [{i}/{len(_scene_plan['execution_order'])}] Creando {obj_type}...")
        
        try:
            # Crear objeto
            created = creation_rules.create_object(
                obj_type, position, collection, material
            )
            
            # Registrar
            for name, obj_data in created.items():
                state_manager.register_object(obj_data.name)
            
            # Validar
            validation = validator.validate_object(
                list(created.values())[0].name
            )
            
            if validation["valid"]:
                obj["status"] = "completed"
                results["success"].append(obj_type)
                print(f"   ✅ {obj_type} creado correctamente")
            else:
                obj["status"] = "warning"
                results["success"].append(obj_type)
                print(f"   ⚠️  {obj_type} creado con warnings: {validation['warnings']}")
            
            # Auto-save después de cada objeto
            state_manager.auto_save()
            
        except Exception as e:
            obj["status"] = "failed"
            results["failed"].append({"type": obj_type, "error": str(e)})
            print(f"   ❌ Error creando {obj_type}: {e}")
    
    # Completar plan
    _scene_plan["status"] = "completed"
    _scene_plan["completed_at"] = datetime.now().isoformat()
    
    # Log
    state_manager.log_action("execute_plan", {
        "plan_name": _scene_plan["name"],
        "success": len(results["success"]),
        "failed": len(results["failed"]),
    })
    
    print(f"\n📊 Resultado: {len(results['success'])} éxitos, {len(results['failed'])} fallos")
    
    return results


# ═══════════════════════════════════════════════════════════════
# PLANTILLAS DE ESCENA
# ═══════════════════════════════════════════════════════════════

SCENE_TEMPLATES = {
    "office": {
        "name": "Oficina",
        "description": "Escena de oficina con escritorio, silla y lámpara",
        "objects": [
            {"type": "floor", "position": (0, 0, 0)},
            {"type": "wall", "position": (0, -5, 0)},
            {"type": "table", "position": (0, 0, 0)},
            {"type": "chair", "position": (0, -0.8, 0)},
            {"type": "lamp", "position": (0.5, 0.3, 0.79)},
            {"type": "book", "position": (-0.3, 0.2, 0.83)},
        ],
    },
    "living_room": {
        "name": "Sala de estar",
        "description": "Escena de sala con mesa, silla y decoración",
        "objects": [
            {"type": "floor", "position": (0, 0, 0)},
            {"type": "wall", "position": (0, -5, 0)},
            {"type": "table", "position": (0, 0, 0)},
            {"type": "chair", "position": (0, -0.8, 0)},
            {"type": "cup", "position": (0.2, 0.1, 0.79)},
            {"type": "pot", "position": (-0.5, 0.3, 0.79)},
        ],
    },
    "kitchen": {
        "name": "Cocina",
        "description": "Escena de cocina con mesa y utensilios",
        "objects": [
            {"type": "floor", "position": (0, 0, 0)},
            {"type": "wall", "position": (0, -5, 0)},
            {"type": "table", "position": (0, 0, 0)},
            {"type": "cup", "position": (0.2, 0.1, 0.79)},
            {"type": "cup", "position": (-0.2, 0.1, 0.79)},
            {"type": "book", "position": (0.4, -0.2, 0.83)},
        ],
    },
}


def load_template(template_name):
    """
    Cargar una plantilla de escena.
    
    Args:
        template_name: Nombre de la plantilla (office, living_room, kitchen)
    
    Returns:
        dict con el plan cargado
    """
    if template_name not in SCENE_TEMPLATES:
        raise ValueError(f"Plantilla no encontrada: {template_name}. Disponibles: {list(SCENE_TEMPLATES.keys())}")
    
    template = SCENE_TEMPLATES[template_name]
    
    # Crear plan
    create_plan(template["name"], template["description"])
    
    # Agregar objetos
    for obj in template["objects"]:
        add_object_to_plan(
            obj["type"],
            obj["position"],
            obj.get("parent"),
            obj.get("anchor"),
            obj.get("collection"),
            obj.get("material"),
        )
    
    print(f"\n📋 Plantilla '{template_name}' cargada: {len(template['objects'])} objetos")
    print_plan()
    
    return get_plan()


# ═══════════════════════════════════════════════════════════════
# UTILIDADES
# ═══════════════════════════════════════════════════════════════

def estimate_time():
    """Estimar tiempo de ejecución del plan."""
    # ~2 segundos por objeto
    object_count = len(_scene_plan["execution_order"])
    estimated_seconds = object_count * 2
    
    minutes = estimated_seconds // 60
    seconds = estimated_seconds % 60
    
    return {
        "objects": object_count,
        "estimated_seconds": estimated_seconds,
        "estimated_time": f"{minutes}m {seconds}s",
    }


def clear_plan():
    """Limpiar el plan actual."""
    _scene_plan["objects"] = []
    _scene_plan["dependencies"] = {}
    _scene_plan["execution_order"] = []
    _scene_plan["status"] = "draft"
    print("[planner] Plan limpiado")


def export_plan(filepath):
    """Exportar plan a JSON."""
    with open(filepath, 'w') as f:
        json.dump(_scene_plan, f, indent=2)
    print(f"[planner] Plan exportado: {filepath}")


def import_plan(filepath):
    """Importar plan desde JSON."""
    global _scene_plan
    with open(filepath, 'r') as f:
        _scene_plan = json.load(f)
    print(f"[planner] Plan importado: {filepath}")
