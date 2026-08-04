"""
handlers.py — Registri perintah untuk server socket Blender.

Setiap nama perintah memetakan ke callable (params: dict -> dict). `_axsock`
beralih ke registri ini saat tidak ada metode `cmd_*` lama, dan rangkaian tes
offline memakai registri yang sama, sehingga permukaan MCP dan tes berbagi
satu sumber kebenaran.

Menargetkan Blender 4.2 LTS .. 5.x. Semua handler aman di background kecuali
docstring menyebutkan lain (fitur khusus UI mengembalikan error jelas di `blender -b`).
"""
from . import modeling, materials, rigging, animation, scene_tools
from . import uv_texture, printing, batch, analysis, geometry_nodes
from . import io_tools

HANDLERS = {}

# ─── Modeling / objects ───────────────────────────────────────────────────────
HANDLERS.update({
    "create_object": modeling.create_object,
    "get_object_info": modeling.get_object_info,
    "delete_object": modeling.delete_object,
    "transform_object": modeling.transform_object,
    "duplicate_object": modeling.duplicate_object,
    "select_object": modeling.select_object,
    "add_modifier": modeling.add_modifier,
    "list_modifiers": modeling.list_modifiers,
    "remove_modifier": modeling.remove_modifier,
    "apply_modifiers": modeling.apply_modifiers,
    "boolean_operation": modeling.boolean_operation,
    "join_objects": modeling.join_objects,
    "merge_by_distance": modeling.merge_by_distance,
    "bevel_mesh": modeling.bevel_mesh,
    "extrude_face": modeling.extrude_face,
    "inset_face": modeling.inset_face,
    "solidify_mesh": modeling.solidify_mesh,
    "clean_mesh": modeling.clean_mesh,
    "create_text": modeling.create_text,
    "create_curve": modeling.create_curve,
    "create_screw_profile": modeling.create_screw_profile,
    "create_empty": modeling.create_empty,
    "subdivide_mesh": modeling.subdivide_mesh,
    "loop_cut": modeling.loop_cut,
    "apply_transform": modeling.apply_transform,
    "model_from_scratch": modeling.model_from_scratch,
})

# ─── Materials / coloring ─────────────────────────────────────────────────────
HANDLERS.update({
    "create_material": materials.create_material,
    "assign_material": materials.assign_material,
    "list_materials": materials.list_materials,
    "set_color": materials.set_color,
    "add_shader_node": materials.add_shader_node,
    "list_shader_nodes": materials.list_shader_nodes,
    "set_node_value": materials.set_node_value,
    "connect_shader_nodes": materials.connect_shader_nodes,
    "remove_shader_node": materials.remove_shader_node,
    "create_image_texture": materials.create_image_texture,
    "assign_image_texture": materials.assign_image_texture,
    "add_vertex_color": materials.add_vertex_color,
    "set_emission": materials.set_emission,
    "set_transparency": materials.set_transparency,
    "colorize_from_scratch": materials.colorize_from_scratch,
})

# ─── Rigging ──────────────────────────────────────────────────────────────────
HANDLERS.update({
    "create_armature": rigging.create_armature,
    "add_bone": rigging.add_bone,
    "remove_bone": rigging.remove_bone,
    "list_bones": rigging.list_bones,
    "rename_bone": rigging.rename_bone,
    "add_vertex_group": rigging.add_vertex_group,
    "assign_vertex_weights": rigging.assign_vertex_weights,
    "remove_vertex_group": rigging.remove_vertex_group,
    "add_constraint": rigging.add_constraint,
    "setup_ik_chain": rigging.setup_ik_chain,
    "auto_rig_weight": rigging.auto_rig_weight,
    "mirror_bones": rigging.mirror_bones,
    "reset_pose": rigging.reset_pose,
    "pose_bone": rigging.pose_bone,
    "add_armature_modifier": rigging.add_armature_modifier,
    "rig_from_scratch": rigging.rig_from_scratch,
})

# ─── Animation ────────────────────────────────────────────────────────────────
HANDLERS.update({
    "insert_keyframe": animation.insert_keyframe,
    "animate_location": animation.animate_location,
    "animate_rotation": animation.animate_rotation,
    "animate_scale": animation.animate_scale,
    "keyframe_animation": animation.keyframe_animation,
    "set_render_range": animation.set_render_range,
    "set_frame": animation.set_frame,
    "create_action": animation.create_action,
    "list_actions": animation.list_actions,
    "set_keyframe_interpolation": animation.set_keyframe_interpolation,
    "add_shape_key": animation.add_shape_key,
    "list_shape_keys": animation.list_shape_keys,
    "add_rigid_body": animation.add_rigid_body,
    "set_gravity": animation.set_gravity,
    "clear_keyframes": animation.clear_keyframes,
    "animate_from_scratch": animation.animate_from_scratch,
})

# ─── Scene / lights / camera / render ────────────────────────────────────────
HANDLERS.update({
    "create_light": scene_tools.create_light,
    "setup_three_point_lighting": scene_tools.setup_three_point_lighting,
    "create_camera": scene_tools.create_camera,
    "set_camera_target": scene_tools.set_camera_target,
    "set_camera_active": scene_tools.set_camera_active,
    "set_render_engine": scene_tools.set_render_engine,
    "set_render_resolution": scene_tools.set_render_resolution,
    "set_render_samples": scene_tools.set_render_samples,
    "set_cycles_device": scene_tools.set_cycles_device,
    "render_frame": scene_tools.render_frame,
    "render_viewport_to_path": scene_tools.render_viewport_to_path,
    "scene_summary": scene_tools.scene_summary,
    "cleanup_scene": scene_tools.cleanup_scene,
    "purge_orphans": scene_tools.purge_orphans,
    "select_by_type": scene_tools.select_by_type,
    "hide_object": scene_tools.hide_object,
    "unhide_all": scene_tools.unhide_all,
    "set_scene_name": scene_tools.set_scene_name,
    "jump_to_view3d_object_by_name": scene_tools.jump_to_view3d_object_by_name,
})

# ─── Import/Export ────────────────────────────────────────────────────────────
HANDLERS.update({
    "list_export_formats": io_tools.list_export_formats,
    "export_scene": io_tools.export_scene,
    "export_selected": io_tools.export_selected,
    "import_file": io_tools.import_file,
})

# ─── UV / texturing ───────────────────────────────────────────────────────────
HANDLERS.update({
    "add_uv_map": uv_texture.add_uv_map,
    "unwrap_object": uv_texture.unwrap_object,
    "list_uv_maps": uv_texture.list_uv_maps,
    "remove_uv_map": uv_texture.remove_uv_map,
    "texel_density": uv_texture.texel_density,
})

# ─── 3D printing ──────────────────────────────────────────────────────────────
HANDLERS.update({
    "check_manifold": printing.check_manifold,
    "set_dimensions_mm": printing.set_dimensions_mm,
    "add_wall_thickness": printing.add_wall_thickness,
    "bed_layout": printing.bed_layout,
    "export_stl_mm": printing.export_stl_mm,
})

# ─── Batch ────────────────────────────────────────────────────────────────────
HANDLERS.update({
    "batch_rename": batch.batch_rename,
    "batch_delete_by_type": batch.batch_delete_by_type,
    "apply_transforms_all": batch.apply_transforms_all,
    "batch_duplicate": batch.batch_duplicate,
    "select_all": batch.select_all,
    "batch_set_scale": batch.batch_set_scale,
    "batch_set_location": batch.batch_set_location,
})

# ─── Analysis ─────────────────────────────────────────────────────────────────
HANDLERS.update({
    "get_objects_summary": analysis.get_objects_summary,
    "get_object_detail_summary": analysis.get_object_detail_summary,
    "get_blendfile_summary_datablocks": analysis.get_blendfile_summary_datablocks,
    "mesh_analysis": analysis.mesh_analysis,
    "analyze_performance": analysis.analyze_performance,
})

# ─── Geometry nodes ───────────────────────────────────────────────────────────
HANDLERS.update({
    "add_geometry_nodes_modifier": geometry_nodes.add_geometry_nodes_modifier,
    "list_gn_modifiers": geometry_nodes.list_gn_modifiers,
    "scatter_instances": geometry_nodes.scatter_instances,
    "gn_add_node": geometry_nodes.gn_add_node,
})



def get_handler(command_name):
    return HANDLERS.get(command_name)


def command_count():
    return len(HANDLERS)


def command_names():
    return sorted(HANDLERS.keys())
