# blender-modeling — Geometry Creation Skill

Create and modify 3D geometry using Blender's primitives and modifiers.

## Primitive Reference

| Object | Code |
|--------|------|
| Cube | `bpy.ops.mesh.primitive_cube_add(size=1, location=(0,0,0))` |
| Sphere | `bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0,0,0))` |
| Cylinder | `bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=2, location=(0,0,0))` |
| Cone | `bpy.ops.mesh.primitive_cone_add(radius1=1, depth=2, location=(0,0,0))` |
| Torus | `bpy.ops.mesh.primitive_torus_add(major_radius=1, minor_radius=0.3, location=(0,0,0))` |

## Modifiers Quick Reference

| Modifier | Code |
|----------|------|
| SubSurf | `mod = obj.modifiers.new(name="Subsurf", type='SUBSURF'); mod.levels = 2` |
| Bevel | `mod = obj.modifiers.new(name="Bevel", type='BEVEL'); mod.width = 0.01` |
| Mirror | `mod = obj.modifiers.new(name="Mirror", type='MIRROR'); mod.use_axis[0] = True` |
| Array | `mod = obj.modifiers.new(name="Array", type='ARRAY'); mod.count = 5` |
| Solidify | `mod = obj.modifiers.new(name="Solidify", type='SOLIDIFY'); mod.thickness = 0.01` |
| Boolean | `mod = obj.modifiers.new(name="Bool", type='BOOLEAN'); mod.operation = 'DIFFERENCE'` |

## Best Practices

- Work in meters (1 Blender unit = 1 meter)
- Apply transforms before adding modifiers
- Name objects descriptively: GEO_table_01, GEO_chair_back
- Use Mirror modifiers for symmetrical objects
- Add SubSurf last for smooth preview
