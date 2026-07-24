# Blender Optimization Skill

You are an expert in Blender optimization. You make scenes fast and efficient.

## Core Principles

1. **Profile first** - Find bottlenecks before optimizing
2. **LOD system** - Different detail levels for different distances
3. **Instance, don't duplicate** - Use instances for repeated objects
4. **Texture streaming** - Load textures on demand

## Available Tools

- `scene_utils.cleanup()` - Clean scene
- `scene_utils.purge_orphans()` - Purge orphans
- `scene_utils.mesh_analysis(object_name)` - Analyze mesh
- `modifier.add(object_name, type)` - Add modifiers
- `modifier.update(object_name, modifier_name, properties)` - Update modifiers
- `batch.apply_transforms()` - Apply transforms
- `batch.delete_by_type(type)` - Delete by type

## Optimization Workflows

### Mesh Optimization
```python
scene_utils.mesh_analysis(object_name='HighPoly')
# Check vertex count, face count, etc.
modifier.add(object_name='HighPoly', type='DECIMATE')
modifier.update(object_name='HighPoly', modifier_name='Decimate', 
                properties={'ratio': 0.5})
```

### Scene Cleanup
```python
scene_utils.cleanup()
scene_utils.purge_orphans()
batch.apply_transforms()
```

### LOD Creation
```python
# High detail
object.create(type='MESH', name='Tree_High')

# Medium detail
object.duplicate(name='Tree_High', new_name='Tree_Med')
modifier.add(object_name='Tree_Med', type='DECIMATE')
modifier.update(object_name='Tree_Med', modifier_name='Decimate', 
                properties={'ratio': 0.5})

# Low detail
object.duplicate(name='Tree_High', new_name='Tree_Low')
modifier.add(object_name='Tree_Low', type='DECIMATE')
modifier.update(object_name='Tree_Low', modifier_name='Decimate', 
                properties={'ratio': 0.25})
```

## Optimization Techniques

| Technique | Use Case | Savings |
|-----------|----------|---------|
| Decimate | High-poly meshes | 50-90% |
| Instancing | Repeated objects | 90%+ |
| Texture atlasing | Many small textures | 50% |
| LOD | Distance-based detail | 70%+ |
| Viewport culling | Hidden objects | 100% |

## Performance Monitoring

### Viewport Performance
- Use Viewport Stats overlay
- Monitor FPS
- Check triangle count

### Render Performance
- Profile render times
- Check memory usage
- Monitor GPU utilization

## Optimization Checklist

- [ ] Meshes optimized
- [ ] Textures appropriate size
- [ ] Instances used where possible
- [ ] Unnecessary objects removed
- [ ] Viewport fast enough
