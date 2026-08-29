import importlib
import math
import sys
from pathlib import Path

import bpy

sys.path.append(str(Path(__file__).resolve().parent / "addon"))

import mesh_builder
import pbr_factory

importlib.reload(mesh_builder)
importlib.reload(pbr_factory)

# 1. Clean Scene
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()

# Materials Setup
mat_metal_dark = pbr_factory.create_pbr_metal(
    "MAT_Luxo_DarkMetal", color=(0.14, 0.15, 0.17), brushed=True
)
mat_metal_chrome = pbr_factory.create_pbr_metal(
    "MAT_Luxo_Chrome", color=(0.85, 0.86, 0.88), brushed=True
)
mat_shade_white = pbr_factory.create_pbr_metal(
    "MAT_Luxo_WhiteEnamel", color=(0.92, 0.92, 0.94), brushed=False
)
mat_spring_steel = pbr_factory.create_pbr_metal(
    "MAT_Luxo_SpringSteel", color=(0.6, 0.62, 0.65), brushed=True
)

# Material Bulb Glass / Emission
mat_bulb = bpy.data.materials.new("MAT_Luxo_Bulb")
mat_bulb.use_nodes = True
nodes = mat_bulb.node_tree.nodes
nodes.clear()
output = nodes.new("ShaderNodeOutputMaterial")
emission = nodes.new("ShaderNodeEmission")
emission.inputs["Color"].default_value = (1.0, 0.96, 0.85, 1.0)
emission.inputs["Strength"].default_value = 25.0
mat_bulb.node_tree.links.new(emission.outputs["Emission"], output.inputs["Surface"])


# ═══════════════════════════════════════════════════════════════
# PIXAR LUXO JR. LAMP — CLEAN WORLD SPACE KINEMATICS
# ═══════════════════════════════════════════════════════════════

# 1. BASE DOME DISK (Flat on XY ground plane, Z up)
base_profile = [
    (0.001, 0.0),
    (0.16, 0.0),
    (0.175, 0.008),
    (0.17, 0.02),
    (0.14, 0.032),
    (0.05, 0.045),
    (0.035, 0.06),
    (0.001, 0.06),
]
base_obj = mesh_builder.create_lathe_mesh(base_profile, segments=48, location=(0, 0, 0))
base_obj.name = "GEO_Luxo_Base"
mesh_builder.apply_professional_finish(base_obj, bevel_width=0.003, subsurf_levels=1)
base_obj.data.materials.append(mat_metal_dark)

# 2. BASE HINGE JOINT (Cylinder along Y axis, Z=0.07)
# Create cylinder along Y axis manually to avoid parent coordinate rotation
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.025, depth=0.05, location=(0, 0, 0.075), rotation=(math.pi / 2, 0, 0)
)
base_joint = bpy.context.active_object
base_joint.name = "GEO_Luxo_BaseJoint"
mesh_builder.apply_professional_finish(base_joint, bevel_width=0.002, subsurf_levels=1)
base_joint.data.materials.append(mat_metal_chrome)

# 3. LOWER ARMS (Twin Chrome Rods, angled forward +25 deg around Y)
theta1_rad = math.radians(25)
l1 = 0.30

for i, offset_y in enumerate([-0.025, 0.025]):
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.005, depth=l1, location=(0, offset_y, 0.075 + l1 / 2.0)
    )
    arm = bpy.context.active_object
    arm.name = f"GEO_Luxo_LowerArm_{i}"
    # Position pivot at bottom
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    arm.location = (0, offset_y, 0.075)
    arm.rotation_euler = (0, theta1_rad, 0)
    mesh_builder.apply_professional_finish(arm, bevel_width=0.001, subsurf_levels=1)
    arm.data.materials.append(mat_metal_chrome)

# 4. ELBOW JOINT
elbow_x = l1 * math.sin(theta1_rad)
elbow_z = 0.075 + l1 * math.cos(theta1_rad)

bpy.ops.mesh.primitive_cylinder_add(
    radius=0.025, depth=0.05, location=(elbow_x, 0, elbow_z), rotation=(math.pi / 2, 0, 0)
)
elbow_joint = bpy.context.active_object
elbow_joint.name = "GEO_Luxo_ElbowJoint"
mesh_builder.apply_professional_finish(elbow_joint, bevel_width=0.002, subsurf_levels=1)
elbow_joint.data.materials.append(mat_metal_chrome)

# 5. UPPER ARMS (Twin Chrome Rods, angled backward -50 deg around Y)
theta2_rad = math.radians(-50)
l2 = 0.28

for i, offset_y in enumerate([-0.020, 0.020]):
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.005, depth=l2, location=(elbow_x, offset_y, elbow_z)
    )
    arm = bpy.context.active_object
    arm.name = f"GEO_Luxo_UpperArm_{i}"
    arm.rotation_euler = (0, theta2_rad, 0)
    mesh_builder.apply_professional_finish(arm, bevel_width=0.001, subsurf_levels=1)
    arm.data.materials.append(mat_metal_chrome)

# 6. HEAD JOINT
head_x = elbow_x + l2 * math.sin(theta2_rad)
head_z = elbow_z + l2 * math.cos(theta2_rad)

bpy.ops.mesh.primitive_cylinder_add(
    radius=0.022, depth=0.045, location=(head_x, 0, head_z), rotation=(math.pi / 2, 0, 0)
)
head_joint = bpy.context.active_object
head_joint.name = "GEO_Luxo_HeadJoint"
mesh_builder.apply_professional_finish(head_joint, bevel_width=0.002, subsurf_levels=1)
head_joint.data.materials.append(mat_metal_dark)

# 7. LAMPSHADE DOME (Conical Shade with lip, facing forward & down)
shade_profile = [
    (0.025, 0.0),
    (0.04, 0.03),
    (0.075, 0.08),
    (0.13, 0.15),
    (0.165, 0.19),
    (0.175, 0.205),
    (0.17, 0.21),
    (0.155, 0.20),
    (0.12, 0.145),
    (0.07, 0.075),
    (0.035, 0.028),
    (0.02, 0.0),
]
shade_obj = mesh_builder.create_lathe_mesh(shade_profile, segments=48, location=(head_x, 0, head_z))
shade_obj.name = "GEO_Luxo_Lampshade"
shade_obj.rotation_euler = (0, math.radians(120), 0)
mesh_builder.apply_professional_finish(shade_obj, bevel_width=0.002, subsurf_levels=1)
shade_obj.data.materials.append(mat_shade_white)

# 8. LIGHT BULB
shade_dir_x = math.sin(math.radians(120))
shade_dir_z = math.cos(math.radians(120))
bulb_x = head_x + 0.07 * shade_dir_x
bulb_z = head_z + 0.07 * shade_dir_z

bpy.ops.mesh.primitive_uv_sphere_add(radius=0.035, location=(bulb_x, 0, bulb_z))
bulb_obj = bpy.context.active_object
bulb_obj.name = "GEO_Luxo_Bulb"
mesh_builder.apply_professional_finish(bulb_obj, bevel_width=0.001, subsurf_levels=1)
bulb_obj.data.materials.append(mat_bulb)

# 9. SPOT LIGHT EMITTER
light_data = bpy.data.lights.new(name="LGT_Luxo_Spot", type="SPOT")
light_data.energy = 800.0
light_data.color = (1.0, 0.95, 0.85)
light_data.spot_size = math.radians(65)
light_obj = bpy.data.objects.new(name="LGT_Luxo_Spot", object_data=light_data)
bpy.context.collection.objects.link(light_obj)
light_obj.location = (bulb_x + 0.02 * shade_dir_x, 0, bulb_z + 0.02 * shade_dir_z)
light_obj.rotation_euler = (0, math.radians(120), 0)


# 10. TENSION SPRINGS
def create_aligned_spring(name, start_pos, height=0.18, radius=0.010, coils=14):
    curve_data = bpy.data.curves.new(name, type="CURVE")
    curve_data.dimensions = "3D"
    curve_data.bevel_depth = 0.0012
    spline = curve_data.splines.new("POLY")
    steps = coils * 16
    spline.points.add(steps - 1)

    for i in range(steps):
        t = i / (steps - 1)
        angle = t * coils * math.pi * 2
        rx = radius * math.cos(angle)
        ry = radius * math.sin(angle)
        rz = t * height
        spline.points[i].co = (rx, ry, rz, 1.0)

    sp_obj = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(sp_obj)
    sp_obj.location = start_pos
    sp_obj.rotation_euler = (0, theta1_rad, 0)
    sp_obj.data.materials.append(mat_spring_steel)
    return sp_obj


create_aligned_spring("GEO_Luxo_Spring_L1", (0.015, -0.025, 0.08))
create_aligned_spring("GEO_Luxo_Spring_R1", (0.015, 0.025, 0.08))

# 11. DESELECT ALL & CONFIGURE CAMERA / VIEWPORT
bpy.ops.object.select_all(action="DESELECT")

cam_obj = bpy.data.objects.get("Camera")
if not cam_obj:
    cam_data = bpy.data.cameras.new("CAM_Luxo_Studio")
    cam_obj = bpy.data.objects.new("CAM_Luxo_Studio", cam_data)
    bpy.context.collection.objects.link(cam_obj)

cam_obj.location = (0.85, -0.95, 0.45)
cam_obj.rotation_euler = (math.radians(72), 0, math.radians(40))
bpy.context.scene.camera = cam_obj

for area in bpy.context.screen.areas:
    if area.type == "VIEW_3D":
        for space in area.spaces:
            if space.type == "VIEW_3D":
                space.region_3d.view_perspective = "PERSP"
                space.shading.type = "MATERIAL"
                space.overlay.show_overlays = False
        area.tag_redraw()

bpy.context.scene.world.use_nodes = True
bg = bpy.context.scene.world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (0.07, 0.08, 0.10, 1.0)
bg.inputs["Strength"].default_value = 1.0

print("PERFECT KINEMATIC LUXO JR. LAMP SETUP COMPLETE!")
