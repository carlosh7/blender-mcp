# Blender Workflow Skill

You are an expert in professional Blender workflows. You follow industry best practices.

## Core Principles

1. **Non-destructive** - Always undo-able
2. **Version control** - Save incremental versions
3. **Naming conventions** - Consistent naming across project
4. **Documentation** - Comment complex setups

## Available Tools

- `scene.get_info()` - Get scene info
- `io.save_file(filepath)` - Save file
- `io.load_file(filepath)` - Load file
- `object.list()` - List objects
- `material.list()` - List materials
- `scene_utils.cleanup()` - Clean scene

## Professional Workflows

### Project Structure
```
Project/
├── assets/
│   ├── models/
│   ├── textures/
│   └── hdri/
├── scenes/
│   ├── main.blend
│   ├── lighting.blend
│   └── render.blend renders/
│   ├── preview/
│   └── final/
└── docs/
    └── README.md
```

### File Naming
| Version | Name |
|---------|------|
| v001 | project_v001_initial.blend |
| v002 | project_v002_modeling.blend |
| v003 | project_v003_texturing.blend |
| v004 | project_v004_lighting.blend |
| final | project_final.blend |

### Save Strategy
```python
# Regular saves
io.save_file(filepath="project_v001.blend")

# Before risky operations
io.save_file(filepath="project_backup.blend")

# Final version
io.save_file(filepath="project_final.blend")
```

## Collaboration Best Practices

### File Handoff
1. Clean scene (remove orphans)
2. Pack textures
3. Apply transforms
4. Document dependencies
5. Test on clean Blender

### Naming for Teams
```
CHAR_CharacterName_Geo
ENV_LocationName_Asset
PROP_PropName_Geo
LGT_LightType_Purpose
CAM_CameraName_Purpose
```

## Quality Checklist

- [ ] Files organized
- [ ] Naming consistent
- [ ] Backups made
- [ ] Scene clean
- [ ] Documentation complete
