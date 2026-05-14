# blender-animation — Animation Skill

Create keyframe animations, actions, and motion.

## Basic Location Animation

```python
obj = bpy.data.objects["GEO_Sphere"]

# Start position
bpy.context.scene.frame_set(1)
obj.location = (0, 0, 0)
obj.keyframe_insert(data_path="location")

# End position
bpy.context.scene.frame_set(60)
obj.location = (5, 0, 3)
obj.keyframe_insert(data_path="location")

# Set render range
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 60
```

## Rotation (Spinning)

```python
import math
obj = bpy.data.objects["GEO_Wheel"]

bpy.context.scene.frame_set(1)
obj.rotation_euler.z = 0
obj.keyframe_insert(data_path="rotation_euler", index=2)

bpy.context.scene.frame_set(60)
obj.rotation_euler.z = math.radians(360 * 3)  # 3 full rotations
obj.keyframe_insert(data_path="rotation_euler", index=2)
```

## Scale Animation

```python
bpy.context.scene.frame_set(1)
obj.scale = (1, 1, 1)
obj.keyframe_insert(data_path="scale")

bpy.context.scene.frame_set(30)
obj.scale = (2, 2, 2)
obj.keyframe_insert(data_path="scale")
```

## Keyframe Interpolation

```python
# Change interpolation for all keyframes
if obj.animation_data and obj.animation_data.action:
    for fcurve in obj.animation_data.action.fcurves:
        for kp in fcurve.keyframe_points:
            kp.interpolation = 'BEZIER'  # or 'LINEAR', 'CONSTANT'
```

## Action Management

```python
# Create action
action = bpy.data.actions.new("WalkCycle")
obj.animation_data_create().action = action

# List actions on object
for action in bpy.data.actions:
    print(action.name, action.users)
```
