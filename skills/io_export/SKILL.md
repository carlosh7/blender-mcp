# Blender I/O Export Skill

You are an expert in Blender file export/import. You handle all 3D file formats.

## Core Principles

1. **Know your target** - Different formats for different uses
2. **Preserve data** - Choose format that keeps what you need
3. **Optimize** - Remove unnecessary data before export
4. **Test imports** - Always verify the exported file

## Available Tools

- `io.export_fbx(filepath, use_selection)` - Export FBX
- `io.export_obj(filepath, use_selection)` - Export OBJ
- `io.export_gltf(filepath, format)` - Export glTF/GLB
- `io.export_stl(filepath, use_selection)` - Export STL
- `io.import_fbx(filepath)` - Import FBX
- `io.import_obj(filepath)` - Import OBJ
- `io.import_gltf(filepath)` - Import glTF
- `io.import_stl(filepath)` - Import STL
- `io.save_file(filepath)` - Save blend file
- `io.load_file(filepath)` - Load blend file

## Format Comparison

| Format | Animation | Materials | Textures | Best For |
|--------|-----------|-----------|----------|----------|
| FBX | ✅ | ✅ | ✅ | Game engines |
| OBJ | ❌ | ✅ | ✅ | Static models |
| glTF/GLB | ✅ | ✅ | ✅ | Web, real-time |
| STL | ❌ | ❌ | ❌ | 3D printing |
| USD | ✅ | ✅ | ✅ | Industry |

## Export Workflows

### Game Engine (Unity/Unreal)
```python
io.export_fbx(filepath='/tmp/model.fbx', use_selection=True)
```

### Web (Three.js)
```python
io.export_gltf(filepath='/tmp/model.glb', format='GLB')
```

### 3D Printing
```python
io.export_stl(filepath='/tmp/model.stl', use_selection=True)
```

### Static Rendering
```python
io.export_obj(filepath='/tmp/model.obj', use_selection=True)
```

### Collaboration
```python
io.export_gltf(filepath='/tmp/model.gltf', format='GLTF_SEPARATE')
```

## Import Workflows

### Import and Setup
```python
io.import_fbx(filepath='/tmp/character.fbx')
# Then apply materials, adjust scale, etc.
```

### Batch Import
```python
for file in files:
    io.import_gltf(filepath=file)
```

## Export Checklist

- [ ] Correct format for target
- [ ] Selection only (if needed)
- [ ] Scale correct
- [ ] Materials included
- [ ] Textures embedded/linked
- [ ] File size acceptable
