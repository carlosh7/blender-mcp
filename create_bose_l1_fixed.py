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
mat_matte_plastic = pbr_factory.create_pbr_metal('MAT_Bose_BlackPlastic', color=(0.08, 0.09, 0.10), brushed=False)
mat_dark_grille = pbr_factory.create_pbr_metal('MAT_Bose_DarkGrille', color=(0.14, 0.15, 0.16), brushed=True)
mat_chrome_logo = pbr_factory.create_pbr_metal('MAT_Bose_ChromeLogo', color=(0.90, 0.91, 0.93), brushed=True)
mat_speaker_cone = pbr_factory.create_pbr_metal('MAT_Bose_SpeakerCone', color=(0.18, 0.19, 0.20), brushed=False)
mat_io_panel = pbr_factory.create_pbr_metal('MAT_Bose_IOPanel', color=(0.05, 0.05, 0.06), brushed=True)

# LED Green Material
mat_led_green = bpy.data.materials.new('MAT_Bose_LED_Green')
mat_led_green.use_nodes = True
nodes = mat_led_green.node_tree.nodes
nodes.clear()
output = nodes.new('ShaderNodeOutputMaterial')
emission = nodes.new('ShaderNodeEmission')
emission.inputs['Color'].default_value = (0.1, 1.0, 0.2, 1.0)
emission.inputs['Strength'].default_value = 10.0
mat_led_green.node_tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])


# ═══════════════════════════════════════════════════════════════
# BOSE L1 MODEL II — CORRECTED FLUSH OUTRIGGER LEGS
# ═══════════════════════════════════════════════════════════════

# 1. POWER STAND CHASSIS (Width = 0.22m, Length = 0.65m, Height = 0.11m)
chassis_w = 0.22
chassis_l = 0.65
chassis_h = 0.11

bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, chassis_h/2.0))
chassis = bpy.context.active_object
chassis.name = 'GEO_Bose_PowerStand_Chassis'
chassis.scale = (chassis_w, chassis_l, chassis_h)
bpy.ops.object.transform_apply(scale=True)
mesh_builder.apply_professional_finish(chassis, bevel_width=0.004, subsurf_levels=1)
chassis.data.materials.append(mat_matte_plastic)

# Front Handle Recess
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.24, 0.08))
handle_pocket = bpy.context.active_object
handle_pocket.name = 'GEO_Bose_HandleRecess'
handle_pocket.scale = (0.12, 0.08, 0.04)
bpy.ops.object.transform_apply(scale=True)
mesh_builder.apply_professional_finish(handle_pocket, bevel_width=0.002, subsurf_levels=1)
handle_pocket.data.materials.append(mat_io_panel)

# Top Column Socket
bpy.ops.mesh.primitive_cylinder_add(radius=0.055, depth=0.03, location=(0, -0.05, 0.115))
socket_ring = bpy.context.active_object
socket_ring.name = 'GEO_Bose_ColumnSocket'
mesh_builder.apply_professional_finish(socket_ring, bevel_width=0.002, subsurf_levels=1)
socket_ring.data.materials.append(mat_matte_plastic)

# Rear I/O Panel Plate
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.18, 0.112))
io_plate = bpy.context.active_object
io_plate.name = 'GEO_Bose_IOPanel'
io_plate.scale = (0.14, 0.22, 0.004)
bpy.ops.object.transform_apply(scale=True)
mesh_builder.apply_professional_finish(io_plate, bevel_width=0.001, subsurf_levels=1)
io_plate.data.materials.append(mat_io_panel)

# Volume Knob & XLR Jack
bpy.ops.mesh.primitive_cylinder_add(radius=0.010, depth=0.012, location=(0.03, 0.16, 0.120))
knob1 = bpy.context.active_object
knob1.name = 'GEO_Bose_Knob_Vol'
mesh_builder.apply_professional_finish(knob1, bevel_width=0.0008, subsurf_levels=1)
knob1.data.materials.append(mat_matte_plastic)

bpy.ops.mesh.primitive_cylinder_add(radius=0.011, depth=0.008, location=(-0.03, 0.16, 0.118))
xlr = bpy.context.active_object
xlr.name = 'GEO_Bose_XLR_Jack'
mesh_builder.apply_professional_finish(xlr, bevel_width=0.0008, subsurf_levels=1)
xlr.data.materials.append(mat_chrome_logo)

bpy.ops.mesh.primitive_cylinder_add(radius=0.003, depth=0.004, location=(0.03, 0.21, 0.118))
led = bpy.context.active_object
led.name = 'GEO_Bose_LED_Signal'
mesh_builder.apply_professional_finish(led, bevel_width=0.0004, subsurf_levels=1)
led.data.materials.append(mat_led_green)

# 2. FLUSH ATTACHED OUTRIGGER LEGS (Connected to chassis side walls X = +-0.11m)
leg_length = 0.26
leg_width = 0.075
leg_height = 0.022

# Left side legs (Inner edge at X = -0.11)
# Center X = -0.11 - leg_length/2.0 = -0.24
# Right side legs (Inner edge at X = +0.11)
# Center X = +0.11 + leg_length/2.0 = +0.24

leg_configs = [
    ('Front_L', -0.24, -0.22, 0.015),
    ('Front_R',  0.24, -0.22, 0.015),
    ('Rear_L',  -0.24,  0.20, 0.015),
    ('Rear_R',   0.24,  0.20, 0.015)
]

for name_tag, lx, ly, lz in leg_configs:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(lx, ly, lz))
    leg = bpy.context.active_object
    leg.name = f'GEO_Bose_Leg_{name_tag}'
    leg.scale = (leg_length, leg_width, leg_height)
    bpy.ops.object.transform_apply(scale=True)
    mesh_builder.apply_professional_finish(leg, bevel_width=0.002, subsurf_levels=1)
    leg.data.materials.append(mat_matte_plastic)

# Hinge Cap Mounts linking Leg to Chassis Side Wall
for side_x in [-0.11, 0.11]:
    for side_y in [-0.22, 0.20]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.015, depth=0.024, location=(side_x, side_y, 0.018))
        hinge = bpy.context.active_object
        hinge.name = 'GEO_Bose_LegHinge'
        mesh_builder.apply_professional_finish(hinge, bevel_width=0.001, subsurf_levels=1)
        hinge.data.materials.append(mat_matte_plastic)


# 3. VERTICAL LINE ARRAY COLUMN
bpy.ops.mesh.primitive_cylinder_add(radius=0.042, depth=0.95, location=(0, -0.05, 0.595))
col_lower = bpy.context.active_object
col_lower.name = 'GEO_Bose_Column_Extension'
col_lower.scale = (1.0, 0.75, 1.0)
bpy.ops.object.transform_apply(scale=True)
mesh_builder.apply_professional_finish(col_lower, bevel_width=0.002, subsurf_levels=1)
col_lower.data.materials.append(mat_matte_plastic)

bpy.ops.mesh.primitive_cylinder_add(radius=0.046, depth=0.03, location=(0, -0.05, 1.085))
coupling = bpy.context.active_object
coupling.name = 'GEO_Bose_ColumnCoupling'
mesh_builder.apply_professional_finish(coupling, bevel_width=0.001, subsurf_levels=1)
coupling.data.materials.append(mat_matte_plastic)

bpy.ops.mesh.primitive_cylinder_add(radius=0.042, depth=0.95, location=(0, -0.05, 1.575))
col_upper = bpy.context.active_object
col_upper.name = 'GEO_Bose_Column_SpeakerArray'
col_upper.scale = (1.0, 0.75, 1.0)
bpy.ops.object.transform_apply(scale=True)
mesh_builder.apply_professional_finish(col_upper, bevel_width=0.002, subsurf_levels=1)
col_upper.data.materials.append(mat_dark_grille)

bpy.ops.mesh.primitive_cylinder_add(radius=0.044, depth=0.02, location=(0, -0.05, 2.06))
top_cap = bpy.context.active_object
top_cap.name = 'GEO_Bose_ColumnTopCap'
mesh_builder.apply_professional_finish(top_cap, bevel_width=0.001, subsurf_levels=1)
top_cap.data.materials.append(mat_matte_plastic)

bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.082, 1.55))
col_logo = bpy.context.active_object
col_logo.name = 'GEO_Bose_LogoBadge_Column'
col_logo.scale = (0.045, 0.003, 0.010)
bpy.ops.object.transform_apply(scale=True)
mesh_builder.apply_professional_finish(col_logo, bevel_width=0.0005, subsurf_levels=1)
col_logo.data.materials.append(mat_chrome_logo)


# 4. B1 SUBWOOFER MODULE
sub_x = -0.42
sub_y = 0.02
sub_z = 0.195

bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sub_x, sub_y, sub_z))
sub_cab = bpy.context.active_object
sub_cab.name = 'GEO_Bose_B1_Cabinet'
sub_cab.scale = (0.26, 0.45, 0.38)
bpy.ops.object.transform_apply(scale=True)
mesh_builder.apply_professional_finish(sub_cab, bevel_width=0.006, subsurf_levels=1)
sub_cab.data.materials.append(mat_matte_plastic)

for b_z in [0.01, 0.38]:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sub_x, sub_y, b_z))
    bmp = bpy.context.active_object
    bmp.name = f'GEO_Bose_B1_Bumper_{b_z}'
    bmp.scale = (0.27, 0.46, 0.025)
    bpy.ops.object.transform_apply(scale=True)
    mesh_builder.apply_professional_finish(bmp, bevel_width=0.003, subsurf_levels=1)
    bmp.data.materials.append(mat_matte_plastic)

bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sub_x, sub_y, 0.385))
sub_handle = bpy.context.active_object
sub_handle.name = 'GEO_Bose_B1_Handle'
sub_handle.scale = (0.08, 0.18, 0.02)
bpy.ops.object.transform_apply(scale=True)
mesh_builder.apply_professional_finish(sub_handle, bevel_width=0.002, subsurf_levels=1)
sub_handle.data.materials.append(mat_io_panel)

bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sub_x, sub_y - 0.226, sub_z))
sub_grille = bpy.context.active_object
sub_grille.name = 'GEO_Bose_B1_FrontGrille'
sub_grille.scale = (0.24, 0.006, 0.34)
bpy.ops.object.transform_apply(scale=True)
mesh_builder.apply_professional_finish(sub_grille, bevel_width=0.002, subsurf_levels=1)
sub_grille.data.materials.append(mat_dark_grille)

for w_z in [sub_z - 0.08, sub_z + 0.08]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.085, depth=0.03, location=(sub_x, sub_y - 0.20, w_z), rotation=(math.pi/2, 0, 0))
    woofer = bpy.context.active_object
    woofer.name = f'GEO_Bose_B1_Woofer_{w_z}'
    mesh_builder.apply_professional_finish(woofer, bevel_width=0.001, subsurf_levels=1)
    woofer.data.materials.append(mat_speaker_cone)

bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sub_x, sub_y - 0.23, sub_z - 0.02))
sub_logo = bpy.context.active_object
sub_logo.name = 'GEO_Bose_LogoBadge_Sub'
sub_logo.scale = (0.075, 0.004, 0.016)
bpy.ops.object.transform_apply(scale=True)
mesh_builder.apply_professional_finish(sub_logo, bevel_width=0.0006, subsurf_levels=1)
sub_logo.data.materials.append(mat_chrome_logo)


# 5. CAMERA & LIGHTING SETUP
bpy.ops.object.select_all(action='DESELECT')

key_light_data = bpy.data.lights.new(name='LGT_Key', type='AREA')
key_light_data.energy = 1200.0
key_light_data.size = 1.5
key_light_data.color = (1.0, 0.98, 0.95)
key_obj = bpy.data.objects.new('LGT_Key', key_light_data)
bpy.context.collection.objects.link(key_obj)
key_obj.location = (1.8, -2.2, 2.4)
key_obj.rotation_euler = (math.radians(55), 0, math.radians(38))

cam_obj = bpy.data.objects.get('Camera')
if not cam_obj:
    cam_data = bpy.data.cameras.new('CAM_Bose_Studio')
    cam_obj = bpy.data.objects.new('CAM_Bose_Studio', cam_data)
    bpy.context.collection.objects.link(cam_obj)

cam_obj.location = (1.8, -2.5, 1.1)
cam_obj.rotation_euler = (math.radians(72), 0, math.radians(34))
cam_obj.data.lens = 28.0

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
bg.inputs['Color'].default_value = (0.12, 0.14, 0.17, 1.0)
bg.inputs['Strength'].default_value = 1.0

print('BOSE L1 MODEL II LEGS FLUSH ATTACHMENT COMPLETED!')
