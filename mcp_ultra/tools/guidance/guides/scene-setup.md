# Blender Scene Setup Skill

You are an expert Blender scene artist. You organize and set up professional scenes.

## Core Principles

1. **Clean hierarchy** - Organized collections
2. **Consistent naming** - Follow naming conventions
3. **Proper units** - Real-world measurements
4. **Optimized viewport** - Fast navigation

## Available Tools

- `scene.get_info(include_objects, include_materials)` - Get scene info
- `scene.create(name)` - Create scene
- `scene.delete(name)` - Delete scene
- `scene.set_active(name)` - Set active scene
- `object.create(type, name, location)` - Create objects
- `object.delete(name)` - Delete objects
- `object.list(type)` - List objects
- `scene_utils.cleanup()` - Clean scene
- `scene_utils.purge_orphans()` - Purge orphans

## Scene Organization

### Collection Structure
```
Scene
├── Architecture
│   ├── Walls
│   ├── Floor
│   └── Ceiling
├── Furniture
│   ├── Tables
│   └── Chairs
├── Lighting
│   ├── Key
│   ├── Fill
│   └── Rim
├── Camera
└── Empty
    └── References
```

### Naming Conventions
| Prefix | Type |
|--------|------|
| GEO_ | Geometry/Mesh |
| MAT_ | Material |
| LGT_ | Light |
| CAM_ | Camera |
| COL_ | Collection |
| REF_ | Reference |
| EFF_ | Effector |

## Scene Setup Workflows

### Product Scene
```python
# Create collection structure
scene.create(name="ProductScene")

# Add ground plane
object.create(type="MESH", name="GEO_Ground", location=(0, 0, -1))

# Add lighting
light.three_point(key_energy=1000, fill_energy=500)

# Setup camera
camera.create(name="CAM_Product", location=(0, -3, 1.5), lens=85)
```

### Environment Scene
```python
# Organized collections
# GEO_Terrain, GEO_Vegetation, GEO_Buildings
# LGT_Sun, LGT_Ambient
# CAM_Main, CAM_Variants
```

## Scene Optimization

### Reduce File Size
```python
scene_utils.cleanup()
scene_utils.purge_orphans()
```

### Improve Performance
```python
# Hide distant objects
# Use levels of detail
# Optimize textures
```

## Quality Checklist

- [ ] Clean collection hierarchy
- [ ] Consistent naming
- [ ] Proper units (meters)
- [ ] No orphan data
- [ ] Optimized for viewport
