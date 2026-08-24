"""
blender-mcp — Doc Generator
Generación automática de documentación para escenas y objetos.

Regla de oro: SIEMPRE documentar lo que se crea.
"""

import json
from datetime import datetime
from pathlib import Path

import bpy

# ═══════════════════════════════════════════════════════════════
# GENERACIÓN DE DOCUMENTACIÓN
# ═══════════════════════════════════════════════════════════════


def generate_scene_doc(output_dir="/tmp/blender_docs"):
    """
    Generar documentación completa de la escena.

    Args:
        output_dir: Directorio de salida

    Returns:
        Ruta del archivo generado
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = Path(output_dir) / f"scene_doc_{timestamp}.md"

    content = _build_scene_documentation()

    with open(filepath, "w") as f:
        f.write(content)

    print(f"[doc] Documentación generada: {filepath}")
    return str(filepath)


def _build_scene_documentation():
    """Construir documentación de la escena."""
    lines = []

    # Header
    lines.append("# Documentación de Escena - Blender MCP")
    lines.append(f"\n*Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    lines.append(f"\n*Archivo: {bpy.data.filepath or 'UNSAVED'}*")

    # Resumen
    lines.append("\n## Resumen")
    lines.append("\n| Métrica | Valor |")
    lines.append("|---------|-------|")
    lines.append(f"| Objetos totales | {len(bpy.data.objects)} |")
    lines.append(f"| Materiales | {len(bpy.data.materials)} |")
    lines.append(f"| Colecciones | {len(bpy.data.collections)} |")
    lines.append(f"| Meshes | {len(bpy.data.meshes)} |")
    lines.append(f"| Curvas | {len(bpy.data.curves)} |")

    # Colecciones
    lines.append("\n## Colecciones")
    for col in bpy.data.collections:
        lines.append(f"\n### {col.name}")
        if col.objects:
            lines.append("\n| Objeto | Tipo | Posición |")
            lines.append("|--------|------|----------|")
            for obj in col.objects:
                loc = obj.location
                lines.append(
                    f"| {obj.name} | {obj.type} | ({loc.x:.2f}, {loc.y:.2f}, {loc.z:.2f}) |"
                )
        else:
            lines.append("\n*(Vacía)*")

    # Objetos sin colección
    uncollected = [obj for obj in bpy.data.objects if not obj.users_collection]
    if uncollected:
        lines.append("\n### Sin Colección")
        lines.append("\n| Objeto | Tipo | Posición |")
        lines.append("|--------|------|----------|")
        for obj in uncollected:
            loc = obj.location
            lines.append(f"| {obj.name} | {obj.type} | ({loc.x:.2f}, {loc.y:.2f}, {loc.z:.2f}) |")

    # Materiales
    lines.append("\n## Materiales")
    for mat in bpy.data.materials:
        lines.append(f"\n### {mat.name}")
        if mat.use_nodes:
            bsdf = None
            for node in mat.node_tree.nodes:
                if node.type == "BSDF_PRINCIPLED":
                    bsdf = node
                    break
            if bsdf:
                color = bsdf.inputs["Base Color"].default_value
                lines.append(f"\n- **Color**: ({color[0]:.2f}, {color[1]:.2f}, {color[2]:.2f})")
                lines.append(f"- **Rugosidad**: {bsdf.inputs['Roughness'].default_value:.2f}")
                lines.append(f"- **Metalicidad**: {bsdf.inputs['Metallic'].default_value:.2f}")

    # Configuración de render
    lines.append("\n## Configuración de Render")
    scene = bpy.context.scene
    lines.append("\n| Parámetro | Valor |")
    lines.append("|-----------|-------|")
    lines.append(f"| Motor | {scene.render.engine} |")
    lines.append(f"| Resolución | {scene.render.resolution_x}x{scene.render.resolution_y} |")
    lines.append(f"| Frames | {scene.frame_start}-{scene.frame_end} |")
    lines.append(f"| FPS | {scene.render.fps} |")

    # Información de cámara
    cameras = [obj for obj in bpy.data.objects if obj.type == "CAMERA"]
    if cameras:
        lines.append("\n## Cámaras")
        for cam in cameras:
            lines.append(f"\n### {cam.name}")
            lines.append(
                f"- **Posición**: ({cam.location.x:.2f}, {cam.location.y:.2f}, {cam.location.z:.2f})"
            )
            lines.append(
                f"- **Rotación**: ({cam.rotation_euler.x:.2f}, {cam.rotation_euler.y:.2f}, {cam.rotation_euler.z:.2f})"
            )

    # Información de luces
    lights = [obj for obj in bpy.data.objects if obj.type == "LIGHT"]
    if lights:
        lines.append("\n## Luces")
        lines.append("\n| Nombre | Tipo | Energía | Posición |")
        lines.append("|--------|------|----------|----------|")
        for light in lights:
            data = light.data
            loc = light.location
            lines.append(
                f"| {light.name} | {data.type} | {data.energy}W | ({loc.x:.1f}, {loc.y:.1f}, {loc.z:.1f}) |"
            )

    # Footer
    lines.append("\n---")
    lines.append("*Generado automáticamente por blender-mcp*")

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
# SPEC SHEET DE OBJETOS
# ═══════════════════════════════════════════════════════════════


def generate_object_spec(object_name, output_dir="/tmp/blender_docs"):
    """
    Generar spec sheet para un objeto específico.

    Args:
        object_name: Nombre del objeto
        output_dir: Directorio de salida

    Returns:
        Ruta del archivo generado
    """
    obj = bpy.data.objects.get(object_name)
    if not obj:
        print(f"[doc] Objeto no encontrado: {object_name}")
        return None

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    filepath = Path(output_dir) / f"spec_{object_name}.md"

    content = _build_object_spec(obj)

    with open(filepath, "w") as f:
        f.write(content)

    print(f"[doc] Spec sheet generada: {filepath}")
    return str(filepath)


def _build_object_spec(obj):
    """Construir spec sheet de un objeto."""
    from .validator import get_bbox

    lines = []

    # Header
    lines.append(f"# Spec Sheet: {obj.name}")
    lines.append(f"\n*Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

    # Información básica
    lines.append("\n## Información Básica")
    lines.append("\n| Propiedad | Valor |")
    lines.append("|-----------|-------|")
    lines.append(f"| Nombre | {obj.name} |")
    lines.append(f"| Tipo | {obj.type} |")
    lines.append(
        f"| Colección | {obj.users_collection[0].name if obj.users_collection else 'Ninguna'} |"
    )
    lines.append(f"| Padre | {obj.parent.name if obj.parent else 'Ninguno'} |")

    # Transformaciones
    lines.append("\n## Transformaciones")
    lines.append("\n| Propiedad | X | Y | Z |")
    lines.append("|-----------|---|---|---|")
    loc = obj.location
    lines.append(f"| Posición | {loc.x:.4f} | {loc.y:.4f} | {loc.z:.4f} |")
    rot = obj.rotation_euler
    lines.append(f"| Rotación | {rot.x:.4f} | {rot.y:.4f} | {rot.z:.4f} |")
    scale = obj.scale
    lines.append(f"| Escala | {scale.x:.4f} | {scale.y:.4f} | {scale.z:.4f} |")

    # Bounding Box
    bb = get_bbox(obj)
    lines.append("\n## Dimensiones")
    lines.append("\n| Propiedad | Valor |")
    lines.append("|-----------|-------|")
    lines.append(f"| Ancho (X) | {bb['size'][0]:.4f}m |")
    lines.append(f"| Profundidad (Y) | {bb['size'][1]:.4f}m |")
    lines.append(f"| Alto (Z) | {bb['size'][2]:.4f}m |")
    lines.append(
        f"| Centro | ({bb['center'][0]:.4f}, {bb['center'][1]:.4f}, {bb['center'][2]:.4f}) |"
    )
    lines.append(f"| Volumen | {bb['size'][0] * bb['size'][1] * bb['size'][2]:.6f}m³ |")

    # Materiales
    if obj.type == "MESH" and obj.data.materials:
        lines.append("\n## Materiales")
        for mat in obj.data.materials:
            lines.append(f"\n### {mat.name}")
            if mat.use_nodes:
                for node in mat.node_tree.nodes:
                    if node.type == "BSDF_PRINCIPLED":
                        color = node.inputs["Base Color"].default_value
                        lines.append(
                            f"- **Color**: ({color[0]:.2f}, {color[1]:.2f}, {color[2]:.2f})"
                        )
                        lines.append(
                            f"- **Rugosidad**: {node.inputs['Roughness'].default_value:.2f}"
                        )
                        lines.append(
                            f"- **Metalicidad**: {node.inputs['Metallic'].default_value:.2f}"
                        )
                        break

    # Hijos
    children = [child for child in bpy.data.objects if child.parent == obj]
    if children:
        lines.append("\n## Componentes")
        lines.append("\n| Componente | Tipo | Posición Local |")
        lines.append("|------------|------|----------------|")
        for child in children:
            local_loc = child.location
            lines.append(
                f"| {child.name} | {child.type} | ({local_loc.x:.4f}, {local_loc.y:.4f}, {local_loc.z:.4f}) |"
            )

    # Footer
    lines.append("\n---")
    lines.append("*Generado automáticamente por blender-mcp*")

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
# CHANGELOG
# ═══════════════════════════════════════════════════════════════


def generate_changelog(actions_log, output_dir="/tmp/blender_docs"):
    """
    Generar changelog desde el log de acciones.

    Args:
        actions_log: Lista de acciones del historial
        output_dir: Directorio de salida

    Returns:
        Ruta del archivo generado
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    filepath = Path(output_dir) / "changelog.md"

    lines = []
    lines.append("# Changelog - Blender MCP")
    lines.append(f"\n*Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    lines.append("\n## Acciones Registradas")
    lines.append("\n| # | Fecha | Acción | Estado |")
    lines.append("|---|-------|--------|--------|")

    for i, action in enumerate(actions_log, 1):
        status = "✅" if action.get("success", True) else "❌"
        timestamp = action.get("timestamp", "N/A")
        action_type = action.get("action", "unknown")
        details = action.get("details", {})

        # Formatear detalles
        if isinstance(details, dict):
            detail_str = ", ".join(f"{k}: {v}" for k, v in details.items())
        else:
            detail_str = str(details)

        lines.append(f"| {i} | {timestamp} | {action_type} | {status} |")
        if detail_str:
            lines.append(f"| | | {detail_str} | |")

    content = "\n".join(lines)

    with open(filepath, "w") as f:
        f.write(content)

    print(f"[doc] Changelog generado: {filepath}")
    return str(filepath)


# ═══════════════════════════════════════════════════════════════
# JSON EXPORT
# ═══════════════════════════════════════════════════════════════


def export_scene_json(output_dir="/tmp/blender_docs"):
    """
    Exportar escena completa a JSON.

    Args:
        output_dir: Directorio de salida

    Returns:
        Ruta del archivo generado
    """
    from .validator import get_bbox

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    filepath = Path(output_dir) / "scene_data.json"

    data = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "file": bpy.data.filepath or "UNSAVED",
        },
        "summary": {
            "objects": len(bpy.data.objects),
            "materials": len(bpy.data.materials),
            "collections": len(bpy.data.collections),
        },
        "collections": {},
        "objects": [],
        "materials": [],
    }

    # Colecciones
    for col in bpy.data.collections:
        data["collections"][col.name] = [obj.name for obj in col.objects]

    # Objetos
    for obj in bpy.data.objects:
        obj_data = {
            "name": obj.name,
            "type": obj.type,
            "location": list(obj.location),
            "rotation": list(obj.rotation_euler),
            "scale": list(obj.scale),
            "parent": obj.parent.name if obj.parent else None,
            "collection": obj.users_collection[0].name if obj.users_collection else None,
        }

        if obj.type == "MESH":
            bb = get_bbox(obj)
            obj_data["bounding_box"] = bb
            obj_data["materials"] = [m.name for m in obj.data.materials]

        data["objects"].append(obj_data)

    # Materiales
    for mat in bpy.data.materials:
        mat_data = {"name": mat.name, "use_nodes": mat.use_nodes}

        if mat.use_nodes:
            for node in mat.node_tree.nodes:
                if node.type == "BSDF_PRINCIPLED":
                    mat_data["color"] = list(node.inputs["Base Color"].default_value)
                    mat_data["roughness"] = node.inputs["Roughness"].default_value
                    mat_data["metallic"] = node.inputs["Metallic"].default_value
                    break

        data["materials"].append(mat_data)

    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

    print(f"[doc] JSON exportado: {filepath}")
    return str(filepath)
