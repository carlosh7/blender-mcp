# blender-cameras — Camera & Framing Skill

Set up, position, and configure cameras for optimal composition.

## Creating a Camera

```python
import math
bpy.ops.object.camera_add(location=(5, -5, 4), rotation=(math.radians(60), 0, math.radians(45)))
cam = bpy.context.active_object
cam.name = "CAM_Main"
cam.data.lens = 50  # 50mm focal length
bpy.context.scene.camera = cam
```

## Focal Length Guide

| Focal Length | Use Case |
|-------------|----------|
| 24-35mm | Wide, environmental, architectural |
| 50mm | Standard, natural perspective |
| 85mm | Portrait, product close-ups |
| 135mm | Telephoto, compressed background |
| 200mm | Macro, detail shots |

## Camera to Target

```python
# Track to target object
target = bpy.data.objects["GEO_Subject"]
constraint = cam.constraints.new(type='TRACK_TO')
constraint.target = target
constraint.track_axis = 'TRACK_NEGATIVE_Z'
constraint.up_axis = 'UP_Y'
```

## Depth of Field

```python
cam.data.dof.use_dof = True
cam.data.dof.focus_object = target
cam.data.dof.aperture_fstop = 2.8  # Lower = more blur
```

## Auto-Framing

```python
bpy.ops.object.select_all(action='DESELECT')
target.select_set(True)
bpy.context.view_layer.objects.active = target
bpy.ops.view3d.camera_to_view_selected()
```
