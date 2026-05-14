# blender-lighting — Lighting Skill

Set up environment and artificial lighting for 3D scenes.

## Three-Point Lighting Setup

```python
import math
# Key light (main, warm)
bpy.ops.object.light_add(type='AREA', location=(3, -2, 4))
key = bpy.context.active_object; key.name = "LGT_Key"
key.data.energy = 500
key.data.color = (1.0, 0.95, 0.9)

# Fill light (cool, softer)
bpy.ops.object.light_add(type='AREA', location=(-3, 2, 3))
fill = bpy.context.active_object; fill.name = "LGT_Fill"
fill.data.energy = 200
fill.data.color = (0.8, 0.85, 1.0)

# Rim/Back light
bpy.ops.object.light_add(type='SPOT', location=(2, 3, 2))
rim = bpy.context.active_object; rim.name = "LGT_Rim"
rim.data.energy = 300
```

## Light Types

| Type | Use Case | Key Params |
|------|----------|------------|
| POINT | Ambient fill, bulbs | energy, radius |
| SUN | Outdoor, directional | energy, angle |
| SPOT | Accent, rim lights | energy, spot_size, spot_blend |
| AREA | Studio, soft light | energy, size, shape |

## HDRI Environment

For realistic environment lighting, use Poly Haven HDRIs:

```
get_polyhaven_status() → download_polyhaven_hdri()
```

## Studio Lighting Presets

- Product: Large softbox key + white fill + rim
- Portrait: Butterfly (key above camera) + fill below
- Dramatic: Single spot from above + negative fill
- Mood: Colored gels on rim lights
