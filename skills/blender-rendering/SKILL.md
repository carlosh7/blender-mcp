# blender-rendering — Render Configuration Skill

Configure render engines, resolution, and output settings.

## Engine Selection

```python
# Cycles (photorealistic, slower)
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128
bpy.context.scene.cycles.device = 'GPU'  # or 'CPU'

# EEVEE (real-time, faster)
bpy.context.scene.render.engine = 'BLENDER_EEVEE'
```

## Resolution

```python
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.resolution_percentage = 100
bpy.context.scene.render.fps = 24
```

## Output Settings

```python
bpy.context.scene.render.filepath = "/path/to/output.png"
bpy.context.scene.render.image_settings.file_format = 'PNG'  # PNG, JPEG, OPEN_EXR
```

## Rendering

```python
# Single frame
bpy.ops.render.render(write_still=True)

# Animation
bpy.ops.render.render(animation=True)
```

## Color Management

```python
scene = bpy.context.scene
scene.view_settings.view_transform = 'Standard'  # or 'Filmic', 'AgX'
scene.view_settings.look = 'None'  # or 'Medium Contrast'
```

## Cycles Sampling Guide

| Quality | Samples | Use Case |
|---------|---------|----------|
| Draft | 32-64 | Preview, iterations |
| Medium | 128-256 | Final product shots |
| High | 512-1024 | Interior, glass, SSS |
| Ultra | 2048+ | Production, film |
