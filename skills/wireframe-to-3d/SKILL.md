# wireframe-to-3d — 2D Wireframe to 3D Model Skill

Convert 2D wireframe sketches or reference images into 3D models.

## Process

1. **Analyze**: Identify the main geometric shapes from the reference
2. **Block out**: Create primitives matching the silhouette
3. **Refine**: Add edge loops, extruded faces, bevels
4. **Detail**: Add subdivision surface for smooth shapes
5. **Validate**: Compare with reference using screenshot

## Techniques

### From Orthographic Reference
```python
# Create from front-view outline using curves
bpy.ops.curve.primitive_bezier_curve_add()
curve = bpy.context.active_object
# Edit curve points to match reference silhouette
# Convert to mesh, extrude for depth
bpy.ops.object.convert(target='MESH')
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.extrude_region_move()
```

### Lathe/Screw from Profile
```python
# Draw half-profile, then use Screw modifier
bpy.ops.curve.primitive_bezier_curve_add()
bpy.ops.object.convert(target='MESH')
mod = bpy.context.active_object.modifiers.new(name="Lathe", type='SCREW')
mod.angle = math.radians(360)
mod.steps = 32
```

### Extrude from SVG Import
```python
bpy.ops.import_curves.svg(filepath="path/to/vector.svg")
# Select imported curves, convert to mesh, extrude
bpy.ops.object.convert(target='MESH')
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.extrude_region_move()
```

## Shape-Specific Approaches

| Shape | Approach |
|-------|----------|
| Symmetrical | Mirror modifier + edge loop modeling |
| Cylindrical | Screw modifier from half-profile |
| Organic | SubSurf + proportional editing |
| Mechanical | Beveled boxes + booleans |
| Curved | Bezier curves + bevel geometry |
