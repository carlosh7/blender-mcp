import importlib
import math
import sys
from pathlib import Path

import bmesh
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
mat_enamel = pbr_factory.create_pbr_metal(
    "MAT_Luxo_EnamelGray", color=(0.78, 0.80, 0.83), brushed=True
)
mat_chrome = pbr_factory.create_pbr_metal("MAT_Luxo_Chrome", color=(0.88, 0.89, 0.92), brushed=True)
mat_dark_steel = pbr_factory.create_pbr_metal(
    "MAT_Luxo_DarkSteel", color=(0.18, 0.20, 0.22), brushed=True
)

# Bulb Glass / Emission
mat_bulb = bpy.data.materials.new("MAT_Luxo_Bulb")
mat_bulb.use_nodes = True
nodes = mat_bulb.node_tree.nodes
nodes.clear()
output = nodes.new("ShaderNodeOutputMaterial")
emission = nodes.new("ShaderNodeEmission")
emission.inputs["Color"].default_value = (1.0, 0.96, 0.88, 1.0)
emission.inputs["Strength"].default_value = 25.0
mat_bulb.node_tree.links.new(emission.outputs["Emission"], output.inputs["Surface"])


# ═══════════════════════════════════════════════════════════════
# HIGH-FIDELITY PIXAR LUXO JR. LAMP (PRO MODELING)
# ═══════════════════════════════════════════════════════════════

# A. STEPPED DISK BASE
base_profile = [
    (0.001, 0.0),
    (0.17, 0.0),
    (0.18, 0.006),
    (0.178, 0.018),
    (0.14, 0.030),
    (0.06, 0.040),
    (0.04, 0.048),
    (0.04, 0.058),
    (0.048, 0.064),
    (0.048, 0.075),
    (0.038, 0.080),
    (0.038, 0.092),
    (0.024, 0.098),
    (0.001, 0.098),
]
base_obj = mesh_builder.create_lathe_mesh(base_profile, segments=64, location=(0, 0, 0))
base_obj.name = "GEO_Luxo_Base"
mesh_builder.apply_professional_finish(base_obj, bevel_width=0.002, subsurf_levels=1)
base_obj.data.materials.append(mat_enamel)

# B. U-SHAPED BASE YOKE FORK & CENTER PIN (p0 = 0.0, 0.0, 0.098)
p0 = (0.0, 0.0, 0.098)

# Center pin
bpy.ops.mesh.primitive_cylinder_add(radius=0.012, depth=0.025, location=(0, 0, 0.105))
pin = bpy.context.active_object
mesh_builder.apply_professional_finish(pin, bevel_width=0.001, subsurf_levels=1)
pin.data.materials.append(mat_chrome)

# U-Fork Base Bracket
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.125))
yoke = bpy.context.active_object
yoke.name = "GEO_Luxo_Yoke"
yoke.scale = (0.020, 0.052, 0.035)
bpy.ops.object.transform_apply(scale=True)
mesh_builder.apply_professional_finish(yoke, bevel_width=0.0015, subsurf_levels=1)
yoke.data.materials.append(mat_enamel)

# Side Pivot Bolts with Round Screw Heads
for offset_y in [-0.028, 0.028]:
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.006, depth=0.008, location=(0, offset_y, 0.125), rotation=(math.pi / 2, 0, 0)
    )
    bolt = bpy.context.active_object
    mesh_builder.apply_professional_finish(bolt, bevel_width=0.0008, subsurf_levels=1)
    bolt.data.materials.append(mat_dark_steel)

# C. LOWER PARALLEL BARS WITH ROUNDED END CAPS
l1 = 0.28
theta1_rad = math.radians(42)

p1 = (p0[0] + l1 * math.sin(theta1_rad), 0.0, p0[2] + 0.027 + l1 * math.cos(theta1_rad))


def create_rounded_arm_bar(name, p_start, p_end, offset_y, width=0.014, thickness=0.004):
    dx = p_end[0] - p_start[0]
    dz = p_end[2] - p_start[2]
    length = math.sqrt(dx * dx + dz * dz)
    pitch = math.atan2(dx, dz)

    # Create flat bar with rounded caps
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bm.to_mesh(mesh)
    bm.free()

    bar = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(bar)
    bar.scale = (width, thickness, length)
    bpy.ops.object.transform_apply(scale=True)

    # Pivot at bottom
    bar.location = ((p_start[0] + p_end[0]) / 2.0, offset_y, (p_start[2] + p_end[2]) / 2.0)
    bar.rotation_euler = (0, pitch, 0)
    mesh_builder.apply_professional_finish(bar, bevel_width=0.001, subsurf_levels=1)
    bar.data.materials.append(mat_enamel)
    return bar


p0_pivot = (p0[0], 0, p0[2] + 0.027)

for i, offset_y in enumerate([-0.022, 0.022]):
    create_rounded_arm_bar(f"GEO_Luxo_LowerBar_{i}", p0_pivot, p1, offset_y)

# D. TRIANGULAR ELBOW MECHANISM PLATES & CONNECTING PINS (At p1)
for offset_y in [-0.026, 0.026]:
    mesh = bpy.data.meshes.new("GEO_Luxo_ElbowPlate")
    bm = bmesh.new()
    v1 = bm.verts.new((-0.03, offset_y, -0.035))
    v2 = bm.verts.new((0.04, offset_y, -0.01))
    v3 = bm.verts.new((-0.015, offset_y, 0.045))
    bm.faces.new([v1, v2, v3])

    bmesh.ops.extrude_face_region(bm, geom=bm.faces)
    bm.to_mesh(mesh)
    bm.free()

    plate_obj = bpy.data.objects.new("GEO_Luxo_ElbowPlate", mesh)
    plate_obj.location = p1
    bpy.context.collection.objects.link(plate_obj)
    mesh_builder.apply_professional_finish(plate_obj, bevel_width=0.0015, subsurf_levels=1)
    plate_obj.data.materials.append(mat_enamel)

# E. UPPER PARALLEL BARS
l2 = 0.25
theta2_rad = math.radians(-38)

p2 = (p1[0] + l2 * math.sin(theta2_rad), 0.0, p1[2] + l2 * math.cos(theta2_rad))

for i, offset_y in enumerate([-0.018, 0.018]):
    create_rounded_arm_bar(f"GEO_Luxo_UpperBar_{i}", p1, p2, offset_y)

# F. HEAD MOUNT SWIVEL JOINT (At p2)
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.016, depth=0.04, location=p2, rotation=(math.pi / 2, 0, 0)
)
head_joint = bpy.context.active_object
head_joint.name = "GEO_Luxo_HeadJoint"
mesh_builder.apply_professional_finish(head_joint, bevel_width=0.0012, subsurf_levels=1)
head_joint.data.materials.append(mat_enamel)

# G. ICONIC TULIP / BELL LAMPSHADE WITH VENTILATION SLOTS & TOP SWITCH
# Smooth acorn/tulip profile: rear cap + rear cylinder with vents + flared bell trumpet + rolled lip rim
shade_profile = [
    (0.001, 0.0),
    (0.02, 0.005),
    (0.038, 0.018),
    (0.042, 0.065),
    (0.05, 0.085),
    (0.07, 0.115),
    (0.098, 0.155),
    (0.125, 0.19),
    (0.132, 0.20),
    (0.128, 0.205),
    (0.12, 0.20),
    (0.09, 0.15),
    (0.06, 0.11),
    (0.044, 0.08),
    (0.036, 0.06),
    (0.034, 0.02),
    (0.015, 0.005),
    (0.001, 0.005),
]
shade_obj = mesh_builder.create_lathe_mesh(shade_profile, segments=64, location=p2)
shade_obj.name = "GEO_Luxo_Lampshade"

shade_pitch_deg = 110
shade_pitch_rad = math.radians(shade_pitch_deg)
shade_obj.rotation_euler = (0, shade_pitch_rad, 0)
mesh_builder.apply_professional_finish(shade_obj, bevel_width=0.0015, subsurf_levels=1)
shade_obj.data.materials.append(mat_enamel)

# Top Turn Switch Knob
shade_dir_x = math.sin(shade_pitch_rad)
shade_dir_z = math.cos(shade_pitch_rad)

bpy.ops.mesh.primitive_cylinder_add(
    radius=0.007, depth=0.016, location=(p2[0] - 0.012, 0, p2[2] + 0.036)
)
knob = bpy.context.active_object
knob.name = "GEO_Luxo_SwitchKnob"
mesh_builder.apply_professional_finish(knob, bevel_width=0.0008, subsurf_levels=1)
knob.data.materials.append(mat_dark_steel)

# 6 Ventilation Slots Cut Around Rear Housing
for s_idx in range(6):
    angle = (s_idx / 6.0) * math.pi * 2
    vx = p2[0] + 0.02 * math.cos(angle)
    vy = 0.025 * math.sin(angle)
    vz = p2[2] + 0.025
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(vx, vy, vz))
    slot = bpy.context.active_object
    slot.name = f"GEO_Luxo_VentSlot_{s_idx}"
    slot.scale = (0.003, 0.014, 0.005)
    bpy.ops.object.transform_apply(scale=True)
    mesh_builder.apply_professional_finish(slot, bevel_width=0.0004, subsurf_levels=1)
    slot.data.materials.append(mat_dark_steel)

# H. BULB & EMISSION LIGHT
bulb_pos = (p2[0] + 0.065 * shade_dir_x, 0.0, p2[2] + 0.065 * shade_dir_z)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.028, location=bulb_pos)
bulb_obj = bpy.context.active_object
bulb_obj.name = "GEO_Luxo_Bulb"
mesh_builder.apply_professional_finish(bulb_obj, bevel_width=0.0008, subsurf_levels=1)
bulb_obj.data.materials.append(mat_bulb)

light_data = bpy.data.lights.new(name="LGT_Luxo_Spot", type="SPOT")
light_data.energy = 900.0
light_data.color = (1.0, 0.96, 0.88)
light_data.spot_size = math.radians(70)
light_obj = bpy.data.objects.new(name="LGT_Luxo_Spot", object_data=light_data)
bpy.context.collection.objects.link(light_obj)
light_obj.location = (bulb_pos[0] + 0.01 * shade_dir_x, 0, bulb_pos[2] + 0.01 * shade_dir_z)
light_obj.rotation_euler = (0, shade_pitch_rad, 0)


# I. DUAL TENSION SPRINGS
def create_aligned_spring(name, start_pos, end_pos, radius=0.006, coils=16):
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
    sp_obj.data.materials.append(mat_enamel)
    return sp_obj


# Lower Springs
sp_start_l = (p0_pivot[0] + 0.006, -0.024, p0_pivot[2] + 0.012)
sp_end_l = (
    p0_pivot[0] + 0.006 + 0.16 * math.sin(theta1_rad),
    -0.024,
    p0_pivot[2] + 0.012 + 0.16 * math.cos(theta1_rad),
)
create_aligned_spring("GEO_Luxo_Spring_Lower_L", sp_start_l, sp_end_l)

sp_start_r = (p0_pivot[0] + 0.006, 0.024, p0_pivot[2] + 0.012)
sp_end_r = (
    p0_pivot[0] + 0.006 + 0.16 * math.sin(theta1_rad),
    0.024,
    p0_pivot[2] + 0.012 + 0.16 * math.cos(theta1_rad),
)
create_aligned_spring("GEO_Luxo_Spring_Lower_R", sp_start_r, sp_end_r)

# Middle Horizontal Spring across elbow plates
sp_mid_start = (p1[0] - 0.018, -0.026, p1[2] - 0.008)
sp_mid_end = (p1[0] + 0.030, -0.026, p1[2] - 0.008)
create_aligned_spring("GEO_Luxo_Spring_Middle", sp_mid_start, sp_mid_end, coils=12)

# J. CAMERA & VIEWPORT SETTINGS
bpy.ops.object.select_all(action="DESELECT")

cam_obj = bpy.data.objects.get("Camera")
if not cam_obj:
    cam_data = bpy.data.cameras.new("CAM_Luxo_Studio")
    cam_obj = bpy.data.objects.new("CAM_Luxo_Studio", cam_data)
    bpy.context.collection.objects.link(cam_obj)

cam_obj.location = (0.70, -0.75, 0.40)
cam_obj.rotation_euler = (math.radians(65), 0, math.radians(43))
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
bg.inputs["Color"].default_value = (0.15, 0.17, 0.22, 1.0)
bg.inputs["Strength"].default_value = 1.0

print("PRO PIXAR LUXO JR. REPLICA COMPLETE!")
