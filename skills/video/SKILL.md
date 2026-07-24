# Blender Video Production Skill

You are an expert in Blender video production. You create videos and animations for final output.

## Core Principles

1. **Plan your shots** - Storyboard before animating
2. **Render in passes** - Separate elements for flexibility
3. **Optimize render time** - Use EEVEE for preview, Cycles for final
4. **Post-production** - Compositing enhances the final product

## Available Tools

- `animation.keyframe_insert(object_name, property, frame)` - Insert keyframe
- `animation.set_keyframe(object_name, property, frame, value)` - Set keyframe
- `animation.play(start, end)` - Play animation
- `animation.stop()` - Stop animation
- `render.render(filepath, engine)` - Render frame/animation
- `render.set_engine(engine)` - Set render engine
- `render.setResolution(width, height)` - Set resolution
- `camera.create(name, location, lens)` - Create camera
- `camera.setResolution(width, height)` - Set camera resolution

## Video Workflows

### Simple Animation
```python
animation.set_keyframe(object_name='Cube', property='location', frame=1, value=(0, 0, 0))
animation.set_keyframe(object_name='Cube', property='location', frame=100, value=(5, 0, 3))
render.setResolution(width=1920, height=1080)
render.render(filepath='/tmp/animation')
```

### Turntable Animation
```python
batch.turntable(object_name='Product', frames=120, axis='Z')
render.setResolution(width=1920, height=1080)
render.render(filepath='/tmp/turntable')
```

### Product Visualization
```python
camera.create(name='MainCam', location=(0, -3, 1.5), lens=85)
light.three_point(key_energy=1000, fill_energy=500, rim_energy=800)
render.set_engine(engine='CYCLES')
render.set_cycles_settings(samples=256, denoising=True)
render.setResolution(width=1920, height=1080)
```

## Resolution Standards

| Format | Resolution | FPS | Use Case |
|--------|------------|-----|----------|
| HD | 1280x720 | 30 | Web |
| Full HD | 1920x1080 | 30 | Standard |
| 4K | 3840x2160 | 30 | UHD |
| Cinema | 2048x1080 | 24 | Film |
| Vertical | 1080x1920 | 30 | Mobile |

## Render Settings

### Preview (Fast)
```python
render.set_engine(engine='BLENDER_EEVEE_NEXT')
render.set_eevee_settings(taa_render_samples=64)
```

### Final (Quality)
```python
render.set_engine(engine='CYCLES')
render.set_cycles_settings(samples=512, denoising=True, use_gpu=True)
```

## Video Export

### Using FFmpeg
```python
# After rendering image sequence
# Use FFmpeg to compile:
# ffmpeg -framerate 30 -i frame_%04d.png -c:v libx264 output.mp4
```

## Quality Checklist

- [ ] Storyboard planned
- [ ] Camera animation smooth
- [ ] Lighting consistent
- [ ] Render quality adequate
- [ ] Output format correct
