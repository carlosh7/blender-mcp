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
mat_gray = pbr_factory.create_pbr_metal(
    "MAT_Luxo_GrayMetal", color=(0.72, 0.74, 0.77), brushed=True
)
mat_chrome = pbr_factory.create_pbr_metal("MAT_Luxo_Chrome", color=(0.88, 0.89, 0.92), brushed=True)
mat_dark_bolt = pbr_factory.create_pbr_metal(
    "MAT_Luxo_DarkBolt", color=(0.2, 0.22, 0.25), brushed=True
)

# Bulb Glass / Emission
mat_bulb = bpy.data.materials.new("MAT_Luxo_Bulb")
mat_bulb.use_nodes = True
nodes = mat_bulb.node_tree.nodes
nodes.clear()
output = nodes.new("ShaderNodeOutputMaterial")
emission = nodes.new("ShaderNodeEmission")
emission.inputs["Color"].default_value = (1.0, 0.97, 0.88, 1.0)
emission.inputs["Strength"].default_value = 25.0
mat_bulb.node_tree.links.new(emission.outputs["Emission"], output.inputs["Surface"])


# ═══════════════════════════════════════════════════════════════
# PERFECT KINEMATIC LUXO JR. LAMP (ORIGIN-BASED 100% CONNECTED)
# ═══════════════════════════════════════════════════════════════


# Helper: Create flat bar with pivot origin at bottom (0,0,0)
def create_arm_bar(name, length, width=0.012, thickness=0.003, location=(0, 0, 0), rotation_y=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, length / 2.0))
    bar = bpy.context.active_object
    bar.name = name
    bar.scale = (width, thickness, length)
    bpy.ops.object.transform_apply(scale=True)

    # Set pivot origin to bottom (0,0,0)
    bpy.context.scene.cursor.location = (0, 0, 0)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")

    bar.location = location
    bar.rotation_euler = (0, rotation_y, 0)
    mesh_builder.apply_professional_finish(bar, bevel_width=0.0008, subsurf_levels=1)
    bar.data.materials.append(mat_gray)
    return bar


# A. BASE DISK (Radius = 0.12m)
base_profile = [
    (0.001, 0.0),
    (0.12, 0.0),
    (0.125, 0.005),
    (0.12, 0.015),
    (0.09, 0.025),
    (0.03, 0.035),
    (0.022, 0.05),
    (0.026, 0.055),
    (0.026, 0.065),
    (0.018, 0.07),
    (0.001, 0.07),
]
base_obj = mesh_builder.create_lathe_mesh(base_profile, segments=48, location=(0, 0, 0))
base_obj.name = "GEO_Luxo_Base"
mesh_builder.apply_professional_finish(base_obj, bevel_width=0.002, subsurf_levels=1)
base_obj.data.materials.append(mat_gray)

# B. LOWER YOKE BRACKET (At Z=0.07)
p0 = (0.0, 0.0, 0.07)

bpy.ops.mesh.primitive_cube_add(size=1.0, location=p0)
yoke = bpy.context.active_object
yoke.name = "GEO_Luxo_Yoke"
yoke.scale = (0.018, 0.045, 0.028)
bpy.ops.object.transform_apply(scale=True)
mesh_builder.apply_professional_finish(yoke, bevel_width=0.0015, subsurf_levels=1)
yoke.data.materials.append(mat_gray)

# Pivot Bolts on Yoke
for offset_y in [-0.024, 0.024]:
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.005, depth=0.006, location=(p0[0], offset_y, p0[2]), rotation=(math.pi / 2, 0, 0)
    )
    bolt = bpy.context.active_object
    bolt.name = "GEO_Luxo_YokeBolt"
    mesh_builder.apply_professional_finish(bolt, bevel_width=0.0008, subsurf_levels=1)
    bolt.data.materials.append(mat_dark_bolt)

# C. LOWER PARALLEL BARS (Pivot at p0, angle theta1 = +40 deg)
l1 = 0.22
theta1_deg = 40
theta1_rad = math.radians(theta1_deg)

for i, offset_y in enumerate([-0.018, 0.018]):
    create_arm_bar(
        f"GEO_Luxo_LowerBar_{i}", l1, location=(p0[0], offset_y, p0[2]), rotation_y=theta1_rad
    )

# D. TRIANGULAR ELBOW HINGE PLATES (At p1)
p1 = (p0[0] + l1 * math.sin(theta1_rad), 0.0, p0[2] + l1 * math.cos(theta1_rad))

for offset_y in [-0.022, 0.022]:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(p1[0], offset_y, p1[2]))
    plate = bpy.context.active_object
    plate.name = f"GEO_Luxo_ElbowPlate_{offset_y}"
    plate.scale = (0.035, 0.003, 0.045)
    bpy.ops.object.transform_apply(scale=True)
    mesh_builder.apply_professional_finish(plate, bevel_width=0.001, subsurf_levels=1)
    plate.data.materials.append(mat_gray)

# E. UPPER PARALLEL BARS (Pivot at p1, angle theta2 = -35 deg)
l2 = 0.20
theta2_deg = -35
theta2_rad = math.radians(theta2_deg)

for i, offset_y in enumerate([-0.015, 0.015]):
    create_arm_bar(
        f"GEO_Luxo_UpperBar_{i}", l2, location=(p1[0], offset_y, p1[2]), rotation_y=theta2_rad
    )

# F. HEAD MOUNT JOINT (At p2)
p2 = (p1[0] + l2 * math.sin(theta2_rad), 0.0, p1[2] + l2 * math.cos(theta2_rad))

bpy.ops.mesh.primitive_cylinder_add(
    radius=0.014, depth=0.035, location=p2, rotation=(math.pi / 2, 0, 0)
)
head_joint = bpy.context.active_object
head_joint.name = "GEO_Luxo_HeadJoint"
mesh_builder.apply_professional_finish(head_joint, bevel_width=0.001, subsurf_levels=1)
head_joint.data.materials.append(mat_gray)

# G. LAMPSHADE WITH TULIP DOME (At p2)
shade_profile = [
    (0.018, 0.0),
    (0.032, 0.0),
    (0.034, 0.045),
    (0.042, 0.06),
    (0.06, 0.09),
    (0.072, 0.12),
    (0.076, 0.145),
    (0.074, 0.15),
    (0.068, 0.146),
    (0.055, 0.118),
    (0.038, 0.058),
    (0.03, 0.042),
    (0.03, 0.005),
    (0.014, 0.0),
]
shade_obj = mesh_builder.create_lathe_mesh(shade_profile, segments=48, location=p2)
shade_obj.name = "GEO_Luxo_Lampshade"

shade_pitch_deg = 115
shade_pitch_rad = math.radians(shade_pitch_deg)
shade_obj.rotation_euler = (0, shade_pitch_rad, 0)
mesh_builder.apply_professional_finish(shade_obj, bevel_width=0.0015, subsurf_levels=1)
shade_obj.data.materials.append(mat_gray)

# Top Switch Knob
shade_dir_x = math.sin(shade_pitch_rad)
shade_dir_z = math.cos(shade_pitch_rad)

bpy.ops.mesh.primitive_cylinder_add(
    radius=0.006, depth=0.014, location=(p2[0] - 0.01, 0, p2[2] + 0.032)
)
knob = bpy.context.active_object
knob.name = "GEO_Luxo_SwitchKnob"
mesh_builder.apply_professional_finish(knob, bevel_width=0.0008, subsurf_levels=1)
knob.data.materials.append(mat_dark_bolt)

# Ventilation Slots on Rear Housing
for s_idx in range(4):
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(p2[0] + 0.006 + s_idx * 0.006, 0, p2[2] + 0.018)
    )
    slot = bpy.context.active_object
    slot.name = f"GEO_Luxo_VentSlot_{s_idx}"
    slot.scale = (0.002, 0.016, 0.004)
    bpy.ops.object.transform_apply(scale=True)
    mesh_builder.apply_professional_finish(slot, bevel_width=0.0004, subsurf_levels=1)
    slot.data.materials.append(mat_dark_bolt)

# H. BULB & LIGHT EMITTER
bulb_pos = (p2[0] + 0.05 * shade_dir_x, 0.0, p2[2] + 0.05 * shade_dir_z)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.025, location=bulb_pos)
bulb_obj = bpy.context.active_object
bulb_obj.name = "GEO_Luxo_Bulb"
mesh_builder.apply_professional_finish(bulb_obj, bevel_width=0.0008, subsurf_levels=1)
bulb_obj.data.materials.append(mat_bulb)

light_data = bpy.data.lights.new(name="LGT_Luxo_Spot", type="SPOT")
light_data.energy = 800.0
light_data.color = (1.0, 0.96, 0.88)
light_data.spot_size = math.radians(70)
light_obj = bpy.data.objects.new(name="LGT_Luxo_Spot", object_data=light_data)
bpy.context.collection.objects.link(light_obj)
light_obj.location = (bulb_pos[0] + 0.01 * shade_dir_x, 0, bulb_pos[2] + 0.01 * shade_dir_z)
light_obj.rotation_euler = (0, shade_pitch_rad, 0)


# I. DUAL TENSION SPRINGS
def create_aligned_spring(name, start_pos, end_pos, radius=0.006, coils=14):
    dx = end_pos[0] - start_pos[0]
    dy = end_pos[1] - start_pos[1]
    dz = end_pos[2] - start_pos[2]
    length = math.sqrt(dx * dx + dy * dy + dz * dz)

    curve_data = bpy.data.curves.new(name, type="CURVE")
    curve_data.dimensions = "3D"
    curve_data.bevel_depth = 0.0010
    spline = curve_data.splines.new("POLY")
    steps = coils * 16
    spline.points.add(steps - 1)

    for i in range(steps):
        t = i / (steps - 1)
        angle = t * coils * math.pi * 2
        rx = radius * math.cos(angle)
        ry = radius * math.sin(angle)
        rz = t * length
        spline.points[i].co = (rx, ry, rz, 1.0)

    sp_obj = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(sp_obj)
    sp_obj.location = start_pos

    pitch = math.atan2(dx, dz)
    sp_obj.rotation_euler = (0, pitch, 0)
    sp_obj.data.materials.append(mat_gray)
    return sp_obj


# Lower Springs
sp_start_l = (p0[0] + 0.008, -0.020, p0[2] + 0.015)
sp_end_l = (
    p0[0] + 0.008 + 0.14 * math.sin(theta1_rad),
    -0.020,
    p0[2] + 0.015 + 0.14 * math.cos(theta1_rad),
)
create_aligned_spring("GEO_Luxo_Spring_Lower_L", sp_start_l, sp_end_l)

sp_start_r = (p0[0] + 0.008, 0.020, p0[2] + 0.015)
sp_end_r = (
    p0[0] + 0.008 + 0.14 * math.sin(theta1_rad),
    0.020,
    p0[2] + 0.015 + 0.14 * math.cos(theta1_rad),
)
create_aligned_spring("GEO_Luxo_Spring_Lower_R", sp_start_r, sp_end_r)

# Middle Horizontal Spring across elbow plates
sp_mid_start = (p1[0] - 0.015, -0.022, p1[2] - 0.008)
sp_mid_end = (p1[0] + 0.025, -0.022, p1[2] - 0.008)
create_aligned_spring("GEO_Luxo_Spring_Middle", sp_mid_start, sp_mid_end, coils=10)

# J. CAMERA FRAME & STUDIO SETUP
bpy.ops.object.select_all(action="DESELECT")

cam_obj = bpy.data.objects.get("Camera")
if not cam_obj:
    cam_data = bpy.data.cameras.new("CAM_Luxo_Studio")
    cam_obj = bpy.data.objects.new("CAM_Luxo_Studio", cam_data)
    bpy.context.collection.objects.link(cam_obj)

cam_obj.location = (0.75, -0.85, 0.35)
cam_obj.rotation_euler = (math.radians(72), 0, math.radians(40))
bpy.context.scene.camera = cam_obj

for area in bpy.context.screen.areas:
    if area.type == "VIEW_3D":
        for space in area.spaces:
            if space.type == "VIEW_3D":
                space.region_3d.view_perspective = "CAMERA"
                space.shading.type = "MATERIAL"
                space.overlay.show_overlays = False
        area.tag_redraw()

bpy.context.scene.world.use_nodes = True
bg = bpy.context.scene.world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (0.14, 0.16, 0.20, 1.0)
bg.inputs["Strength"].default_value = 1.0

print("PERFECT KINEMATIC LUXO JR. REPLICA COMPLETED!")
