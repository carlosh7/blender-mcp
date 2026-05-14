# blender-materials — PBR Materials Skill

Create and apply physically-based materials using Principled BSDF.

## Quick Material Recipes

### Metallic (Gold)
```python
mat = bpy.data.materials.new(name="MAT_Gold")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (1.0, 0.84, 0.0, 1.0)
bsdf.inputs["Metallic"].default_value = 1.0
bsdf.inputs["Roughness"].default_value = 0.2
```

### Glass
```python
bsdf.inputs["Base Color"].default_value = (0.9, 0.95, 1.0, 1.0)
bsdf.inputs["Metallic"].default_value = 0.0
bsdf.inputs["Roughness"].default_value = 0.0
bsdf.inputs["Transmission Weight"].default_value = 1.0
bsdf.inputs["IOR"].default_value = 1.45
```

### Wood
```python
bsdf.inputs["Base Color"].default_value = (0.55, 0.35, 0.15, 1.0)
bsdf.inputs["Roughness"].default_value = 0.6
bsdf.inputs["Metallic"].default_value = 0.0
```

### Emission (Glow)
```python
bsdf.inputs["Emission Color"].default_value = (1.0, 0.5, 0.0, 1.0)
bsdf.inputs["Emission Strength"].default_value = 5.0
```

## PBR Map Guide

| Map Type | Principled Input | Color Space |
|----------|-----------------|-------------|
| Albedo/Color | Base Color | sRGB |
| Roughness | Roughness | Non-Color |
| Metallic | Metallic | Non-Color |
| Normal | Normal (via Normal Map node) | Non-Color |
| Ambient Occlusion | Mix multiply with Base Color | Non-Color |
| Displacement | Displacement (via Displacement node) | Non-Color |

## Applying Materials

```python
obj = bpy.data.objects["GEO_Table"]
if obj.data.materials:
    obj.data.materials[0] = mat
else:
    obj.data.materials.append(mat)
```
