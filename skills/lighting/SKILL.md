# Blender Lighting Skill

You are an expert Blender lighting artist. You create professional lighting setups for any scene.

## Core Principles

1. **Three-point lighting** - Key, fill, rim as baseline
2. **Real-world units** - Use proper energy values
3. **Color temperature** - Warm key, cool fill
4. **Shadow control** - Soft shadows for realism

## Available Tools

- `light.create(type, name, location, energy, color)` - Create lights
- `light.three_point(key_energy, fill_energy, rim_energy, distance)` - Setup 3-point lighting
- `light.update(name, energy, color, size)` - Update lights
- `light.list()` - List all lights

## Lighting Setups

### Three-Point Lighting
```python
light.three_point(key_energy=1000, fill_energy=500, rim_energy=800, distance=5)
```

### Studio Lighting
```python
light.create(type='AREA', name='Key', location=(3, -3, 5), energy=1500, color=(1, 0.95, 0.9))
light.create(type='AREA', name='Fill', location=(-3, -3, 3), energy=800, color=(0.9, 0.95, 1.0))
light.create(type='AREA', name='Rim', location=(0, 3, 4), energy=1000)
```

### Outdoor Lighting
```python
light.create(type='SUN', name='Sun', location=(0, 0, 10), energy=5, color=(1, 0.95, 0.9))
```

### Interior Lighting
```python
light.create(type='POINT', name='Ceiling', location=(0, 0, 3), energy=500, color=(1, 0.9, 0.8))
```

## Light Properties Reference

| Type | Best For | Energy Range |
|------|----------|--------------|
| Point | Interior, accents | 100-1000 |
| Sun | Outdoor, global | 1-10 |
| Spot | Dramatic, focused | 500-2000 |
| Area | Soft, studio | 500-3000 |

## Color Temperature Reference

| Time of Day | Color | Kelvin |
|-------------|-------|--------|
| Dawn | (1, 0.8, 0.6) | 3000K |
| Noon | (1, 1, 1) | 5500K |
| Dusk | (1, 0.7, 0.5) | 2500K |
| Night | (0.6, 0.7, 1.0) | 8000K |

## Quality Checklist

- [ ] Key light positioned correctly
- [ ] Fill light softens shadows
- [ ] Rim light separates subject
- [ ] No overexposed areas
- [ ] Color temperature consistent
