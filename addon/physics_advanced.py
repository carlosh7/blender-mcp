"""
blender-mcp — Physics Advanced Engine (Production Grade)
Motor de física profesional: Cloth pinning, Rigid Body Constraints (Hinge/6DOF), y Bake de simulación a memoria.
"""
try:
    import bpy
    import mathutils
except ImportError:
    bpy = None
    mathutils = None

def cloth_simulation(obj, preset="cotton", pin_top_edges=True):
    """
    Configurar simulación de tela avanzada con grupo de fijación (Pinning) y colisiones internas.
    """
    if bpy is None or obj is None or obj.type != 'MESH':
        return False
    
    presets = {
        "cotton": {"mass": 0.3, "tension": 15.0, "compression": 15.0, "bending": 5.0},
        "silk": {"mass": 0.1, "tension": 5.0, "compression": 5.0, "bending": 1.0},
        "leather": {"mass": 0.6, "tension": 30.0, "compression": 30.0, "bending": 15.0},
        "rubber": {"mass": 0.4, "tension": 10.0, "compression": 10.0, "bending": 2.0},
    }
    params = presets.get(preset, presets["cotton"])
    
    # Agregar o reutilizar modificador Cloth
    mod = obj.modifiers.get("Cloth") or obj.modifiers.new("Cloth", 'CLOTH')
    mod.settings.mass = params["mass"]
    mod.settings.tension_stiffness = params["tension"]
    mod.settings.compression_stiffness = params["compression"]
    mod.settings.bending_stiffness = params["bending"]
    
    # Auto Colisión de tela
    mod.collision_settings.use_collision = True
    mod.collision_settings.use_self_collision = True
    mod.collision_settings.self_distance_min = 0.015
    
    # Crear grupo de fijación (Pinning) si se solicita
    if pin_top_edges:
        vg = obj.vertex_groups.get("PinGroup") or obj.vertex_groups.new(name="PinGroup")
        top_verts = [v.index for v in obj.data.vertices if v.co.z >= (max(v.co.z for v in obj.data.vertices) - 0.05)]
        if top_verts:
            vg.add(top_verts, 1.0, 'REPLACE')
            mod.settings.vertex_group_mass = "PinGroup"
    
    print(f"Simulación Cloth profesional configurada en {obj.name} con preset={preset}")
    return True

def rigid_body_constraint(obj_a, obj_b, constraint_type='HINGE', location=(0, 0, 0)):
    """
    Crear una restricción de cuerpo rígido (Rigid Body Constraint) entre dos objetos.
    """
    if bpy is None or obj_a is None or obj_b is None:
        return False
    
    # Asegurar World Rigid Body
    if not bpy.context.scene.rigidbody_world:
        bpy.ops.rigidbody.world_add()
    
    # Asegurar que ambos objetos sean Rigid Body
    for o in [obj_a, obj_b]:
        if not o.rigid_body:
            bpy.context.view_layer.objects.active = o
            o.select_set(True)
            bpy.ops.rigidbody.object_add()
            o.select_set(False)
    
    # Crear Empty para la restricción
    cb_name = f"RBC_{constraint_type}_{obj_a.name}_{obj_b.name}"
    rbc_empty = bpy.data.objects.new(cb_name, None)
    bpy.context.collection.objects.link(rbc_empty)
    rbc_empty.location = location
    
    bpy.context.view_layer.objects.active = rbc_empty
    rbc_empty.select_set(True)
    bpy.ops.rigidbody.constraint_add()
    
    con = rbc_empty.rigidbody_constraint
    con.type = constraint_type
    con.object1 = obj_a
    con.object2 = obj_b
    
    print(f"Restricción Rigid Body ({constraint_type}) creada entre {obj_a.name} y {obj_b.name}")
    return rbc_empty

def bake_physics_cache(frame_start=1, frame_end=250):
    """
    Hornear (Bake) todas las simulaciones de física de la escena a memoria cache.
    """
    if bpy is None:
        return False
    
    bpy.context.scene.frame_start = frame_start
    bpy.context.scene.frame_end = frame_end
    
    try:
        for override in bpy.context.screen.areas if bpy.context.screen else []:
            if override.type == 'PROPERTIES':
                with bpy.context.temp_override(area=override):
                    bpy.ops.ptcache.bake_all(bake=True)
                break
        print(f"Bake de físicas completado para frames {frame_start} a {frame_end}")
        return True
    except Exception as e:
        print(f"Bake cache info: {e}")
        return False
