# blender-export — Export Skill

Export 3D models in various formats for web, game engines, and 3D printing.

## Available Formats

| Format | Operator | Use Case |
|--------|----------|----------|
| GLB | `export_scene.gltf` | Web, Three.js, Unity |
| GLTF (separate) | `export_scene.gltf` | Web with textures |
| FBX | `export_scene.fbx` | Unity, Unreal, Maya |
| OBJ | `export_scene.obj` | Universal, CAD |
| STL | `export_mesh.stl` | 3D Printing |
| USD | `export_scene.usd` | Pixar, Apple |
| DAE | `export_scene.dae` | COLLADA, legacy |
| PLY | `export_mesh.ply` | Point clouds |

## Export Examples

### GLB (Web/Three.js)
```python
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(
    filepath="/path/to/model.glb",
    export_format='GLB',
    export_texcoords=True,
    export_normals=True,
    export_materials='EXPORT',
)
```

### FBX (Unity/Unreal)
```python
bpy.ops.export_scene.fbx(
    filepath="/path/to/model.fbx",
    use_selection=True,
    apply_scale_options='FBX_SCALE_UNITS',
)
```

### STL (3D Printing)
```python
bpy.ops.export_mesh.stl(
    filepath="/path/to/model.stl",
    use_selection=True,
    global_scale=1000.0,  # Convert to mm
)
```

## Pre-Export Checklist

- [ ] Apply transforms (location, rotation, scale)
- [ ] Apply modifiers if needed
- [ ] Name objects and materials clearly
- [ ] Remove unused data blocks (purge_orphans())
- [ ] Check manifold for 3D printing (check_manifold())
- [ ] Set correct units and scale
