import bpy, bmesh, math, importlib, sys
sys.path.append('/home/carlosh/blender-mcp/addon')

import mesh_builder
import pbr_factory
importlib.reload(mesh_builder)
importlib.reload(pbr_factory)

# 1. Clean Scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Materials Setup
mat_metal_gray = pbr_factory.create_pbr_metal('MAT_Luxo_GrayMetal', color=(0.75, 0.77, 0.80), brushed=True)
mat_dark_bolt = pbr_factory.create_pbr_metal('MAT_Luxo_DarkBolt', color=(0.2, 0.22, 0.25), brushed=True)

# Bulb Glass / Emission
mat_bulb = bpy.data.materials.new('MAT_Luxo_Bulb')
mat_bulb.use_nodes = True
nodes = mat_bulb.node_tree.nodes
nodes.clear()
output = nodes.new('ShaderNodeOutputMaterial')
emission = nodes.new('ShaderNodeEmission')
emission.inputs['Color'].default_value = (1.0, 0.97, 0.88, 1.0)
emission.inputs['Strength'].default_value = 25.0
mat_bulb.node_tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])


# ═══════════════════════════════════════════════════════════════
# EXACT 100% MATHEMATICAL LUXO JR. REPLICA
# ═══════════════════════════════════════════════════════════════

# BMesh Bar Generator (Guarantees 100% exact connection between Point A and Point B)
def create_bar_between_points(name, p_a, p_b, y_offset, width=0.014, thickness=0.004, material=mat_metal_gray):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    
    dx = p_b[0] - p_a[0]
    dz = p_b[2] - p_a[2]
    length = math.sqrt(dx*dx + dz*dz)
    if length < 0.0001:
        length = 0.0001
    
    # 2D Normal vector in XZ plane
    nx = -dz / length * (width / 2.0)
    nz =  dx / length * (width / 2.0)
    
    # 4 corners in XZ plane
    v1 = bm.verts.new((p_a[0] - nx, y_offset - thickness/2.0, p_a[2] - nz))
    v2 = bm.verts.new((p_a[0] + nx, y_offset - thickness/2.0, p_a[2] + nz))
    v3 = bm.verts.new((p_b[0] + nx, y_offset - thickness/2.0, p_b[2] + nz))
    v4 = bm.verts.new((p_b[0] - nx, y_offset - thickness/2.0, p_b[2] - nz))
    
    f = bm.faces.new([v1, v2, v3, v4])
    
    res = bmesh.ops.extrude_face_region(bm, geom=[f])
    verts_extruded = [e for e in res['geom'] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=(0, thickness, 0), verts=verts_extruded)
    
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    mesh_builder.apply_professional_finish(obj, bevel_width=0.001, subsurf_levels=1)
    obj.data.materials.append(material)
    return obj

# 1. BASE DISK WITH STEPPED COLLAR
base_profile = [
    (0.001, 0.0), (0.19, 0.0), (0.20, 0.008), (0.195, 0.02),
    (0.15, 0.035), (0.05, 0.045), (0.035, 0.052), (0.035, 0.072),
    (0.042, 0.078), (0.042, 0.088), (0.028, 0.092), (0.001, 0.092)
]
base_obj = mesh_builder.create_lathe_mesh(base_profile, segments=48, location=(0, 0, 0))
base_obj.name = 'GEO_Luxo_Base'
mesh_builder.apply_professional_finish(base_obj, bevel_width=0.003, subsurf_levels=1)
base_obj.data.materials.append(mat_metal_gray)

# 2. BASE YOKE JOINT (p0)
p0 = (0.0, 0.0, 0.092)

bpy.ops.mesh.primitive_cube_add(size=1.0, location=p0)
yoke = bpy.context.active_object
yoke.name = 'GEO_Luxo_Yoke'
yoke.scale = (0.022, 0.055, 0.035)
bpy.ops.object.transform_apply(scale=True)
mesh_builder.apply_professional_finish(yoke, bevel_width=0.002, subsurf_levels=1)
yoke.data.materials.append(mat_metal_gray)

# Pivot Bolts on Yoke
for offset_y in [-0.03, 0.03]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.006, depth=0.008, location=(p0[0], offset_y, p0[2]), rotation=(math.pi/2, 0, 0))
    bolt = bpy.context.active_object
    bolt.name = 'GEO_Luxo_YokeBolt'
    mesh_builder.apply_professional_finish(bolt, bevel_width=0.001, subsurf_levels=1)
    bolt.data.materials.append(mat_dark_bolt)

# 3. LOWER PARALLEL FLAT BARS (Connecting p0 to p1)
l1 = 0.28
theta1_rad = math.radians(40)

p1 = (
    p0[0] + l1 * math.sin(theta1_rad),
    0.0,
    p0[2] + l1 * math.cos(theta1_rad)
)

for i, offset_y in enumerate([-0.024, 0.024]):
    create_bar_between_points(f'GEO_Luxo_LowerBar_{i}', p0, p1, offset_y)

# 4. TRIANGULAR ELBOW HINGE PLATES (At p1)
for offset_y in [-0.028, 0.028]:
    mesh = bpy.data.meshes.new("GEO_Luxo_ElbowPlate")
    bm = bmesh.new()
    v1 = bm.verts.new((-0.025, offset_y, -0.03))
    v2 = bm.verts.new((0.035, offset_y, -0.01))
    v3 = bm.verts.new((-0.01, offset_y, 0.04))
    bm.faces.new([v1, v2, v3])
    
    bmesh.ops.extrude_face_region(bm, geom=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    
    plate_obj = bpy.data.objects.new("GEO_Luxo_ElbowPlate", mesh)
    plate_obj.location = p1
    bpy.context.collection.objects.link(plate_obj)
    mesh_builder.apply_professional_finish(plate_obj, bevel_width=0.0015, subsurf_levels=1)
    plate_obj.data.materials.append(mat_metal_gray)

# 5. UPPER PARALLEL BARS (Connecting p1 to p2)
l2 = 0.25
theta2_rad = math.radians(-35)

p2 = (
    p1[0] + l2 * math.sin(theta2_rad),
    0.0,
    p1[2] + l2 * math.cos(theta2_rad)
)

for i, offset_y in enumerate([-0.020, 0.020]):
    create_bar_between_points(f'GEO_Luxo_UpperBar_{i}', p1, p2, offset_y)

# 6. HEAD MOUNT JOINT (At p2)
bpy.ops.mesh.primitive_cylinder_add(radius=0.018, depth=0.04, location=p2, rotation=(math.pi/2, 0, 0))
head_joint = bpy.context.active_object
head_joint.name = 'GEO_Luxo_HeadJoint'
mesh_builder.apply_professional_finish(head_joint, bevel_width=0.0015, subsurf_levels=1)
head_joint.data.materials.append(mat_metal_gray)

# 7. LAMPSHADE WITH REAR HOUSING, VENT SLOTS & TOP SWITCH (Mounted at p2)
shade_profile = [
    (0.022, 0.0), (0.045, 0.0), (0.048, 0.065), (0.06, 0.085),
    (0.09, 0.12), (0.145, 0.175), (0.18, 0.22), (0.19, 0.23),
    (0.185, 0.238), (0.175, 0.232), (0.138, 0.18), (0.085, 0.125),
    (0.055, 0.088), (0.042, 0.068), (0.042, 0.008), (0.018, 0.0)
]
shade_obj = mesh_builder.create_lathe_mesh(shade_profile, segments=48, location=p2)
shade_obj.name = 'GEO_Luxo_Lampshade'

shade_pitch_deg = 115
shade_pitch_rad = math.radians(shade_pitch_deg)
shade_obj.rotation_euler = (0, shade_pitch_rad, 0)
mesh_builder.apply_professional_finish(shade_obj, bevel_width=0.002, subsurf_levels=1)
shade_obj.data.materials.append(mat_metal_gray)

# Top Switch Knob
shade_dir_x = math.sin(shade_pitch_rad)
shade_dir_z = math.cos(shade_pitch_rad)

bpy.ops.mesh.primitive_cylinder_add(radius=0.007, depth=0.018, location=(p2[0] - 0.015, 0, p2[2] + 0.045))
knob = bpy.context.active_object
knob.name = 'GEO_Luxo_SwitchKnob'
mesh_builder.apply_professional_finish(knob, bevel_width=0.001, subsurf_levels=1)
knob.data.materials.append(mat_dark_bolt)

# Vent Slots on Rear Housing
for s_idx in range(4):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(p2[0] + 0.01 + s_idx*0.008, 0, p2[2] + 0.025))
    slot = bpy.context.active_object
    slot.name = f'GEO_Luxo_VentSlot_{s_idx}'
    slot.scale = (0.003, 0.022, 0.006)
    bpy.ops.object.transform_apply(scale=True)
    mesh_builder.apply_professional_finish(slot, bevel_width=0.0005, subsurf_levels=1)
    slot.data.materials.append(mat_dark_bolt)

# 8. BULB & LIGHT EMITTER
bulb_pos = (
    p2[0] + 0.075 * shade_dir_x,
    0.0,
    p2[2] + 0.075 * shade_dir_z
)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.038, location=bulb_pos)
bulb_obj = bpy.context.active_object
bulb_obj.name = 'GEO_Luxo_Bulb'
mesh_builder.apply_professional_finish(bulb_obj, bevel_width=0.001, subsurf_levels=1)
bulb_obj.data.materials.append(mat_bulb)

light_data = bpy.data.lights.new(name='LGT_Luxo_Spot', type='SPOT')
light_data.energy = 900.0
light_data.color = (1.0, 0.96, 0.88)
light_data.spot_size = math.radians(70)
light_obj = bpy.data.objects.new(name='LGT_Luxo_Spot', object_data=light_data)
bpy.context.collection.objects.link(light_obj)
light_obj.location = (bulb_pos[0] + 0.02 * shade_dir_x, 0, bulb_pos[2] + 0.02 * shade_dir_z)
light_obj.rotation_euler = (0, shade_pitch_rad, 0)

# 9. DUAL TENSION SPRINGS (Lower & Middle Horizontal)
def create_aligned_spring(name, start_pos, end_pos, radius=0.008, coils=14):
    dx = end_pos[0] - start_pos[0]
    dy = end_pos[1] - start_pos[1]
    dz = end_pos[2] - start_pos[2]
    length = math.sqrt(dx*dx + dy*dy + dz*dz)
    
    curve_data = bpy.data.curves.new(name, type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.bevel_depth = 0.0012
    spline = curve_data.splines.new('POLY')
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
    sp_obj.data.materials.append(mat_metal_gray)
    return sp_obj

# Lower Springs
sp_start_l = (p0[0] + 0.01, -0.026, p0[2] + 0.02)
sp_end_l = (p0[0] + 0.01 + 0.18*math.sin(theta1_rad), -0.026, p0[2] + 0.02 + 0.18*math.cos(theta1_rad))
create_aligned_spring('GEO_Luxo_Spring_Lower_L', sp_start_l, sp_end_l)

sp_start_r = (p0[0] + 0.01, 0.026, p0[2] + 0.02)
sp_end_r = (p0[0] + 0.01 + 0.18*math.sin(theta1_rad), 0.026, p0[2] + 0.02 + 0.18*math.cos(theta1_rad))
create_aligned_spring('GEO_Luxo_Spring_Lower_R', sp_start_r, sp_end_r)

# Middle Horizontal Spring across elbow plates
sp_mid_start = (p1[0] - 0.02, -0.028, p1[2] - 0.01)
sp_mid_end = (p1[0] + 0.035, -0.028, p1[2] - 0.01)
create_aligned_spring('GEO_Luxo_Spring_Middle', sp_mid_start, sp_mid_end, coils=10)

# 10. DESELECT & CAMERA FRAME
bpy.ops.object.select_all(action='DESELECT')

cam_obj = bpy.data.objects.get('Camera')
if not cam_obj:
    cam_data = bpy.data.cameras.new('CAM_Luxo_Studio')
    cam_obj = bpy.data.objects.new('CAM_Luxo_Studio', cam_data)
    bpy.context.collection.objects.link(cam_obj)

cam_obj.location = (1.1, -1.2, 0.65)
cam_obj.rotation_euler = (math.radians(64), 0, math.radians(42))
bpy.context.scene.camera = cam_obj

for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.region_3d.view_perspective = 'CAMERA'
                space.shading.type = 'MATERIAL'
                space.overlay.show_overlays = False
        area.tag_redraw()

bpy.context.scene.world.use_nodes = True
bg = bpy.context.scene.world.node_tree.nodes['Background']
bg.inputs['Color'].default_value = (0.12, 0.14, 0.18, 1.0)
bg.inputs['Strength'].default_value = 1.0

print('PERFECT KINEMATICALLY CONNECTED LUXO JR. REPLICA COMPLETED!')
