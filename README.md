# blender-mcp-ultra

**MCP server para Blender** — 165 tools del registry (171 vía MCP), headless, multi-agente.

> Estado: **beta funcional**. Verificado E2E en Blender 5.1; ver `docs/skills/` para recetas probadas.

## Overview

blender-mcp-ultra connects Blender to any AI assistant (Claude, Cursor, Windsurf, opencode) via the Model Context Protocol (MCP). It provides comprehensive control over Blender with production-grade security and performance.

## Features

- **165 tools** en 21 módulos (modelado por componentes, animación, física, compositor, render por jobs)
- **19 Skills** for Claude Code/Cursor
- **Enterprise Security**: AST validation, sandboxed execution, rate limiting
- **Multi-Provider**: OpenAI, Anthropic, Google, DeepSeek, Ollama
- **Asset Integration**: PolyHaven, Sketchfab
- **Clean Architecture**: Modular, testable, maintainable
- **Performance**: LRU cache, lazy loading, connection pooling

## Quick Start

### Prerequisites

- Python 3.10+
- Blender 4.0+ (or 5.2 LTS)
- An MCP client (Claude Desktop, Cursor, opencode, etc.)

### Installation

```bash
# Clone the repository
git clone https://github.com/carlosh7/blender-mcp-ultra.git
cd blender-mcp-ultra

# Install dependencies
pip install -e .

# Run tests
python test_all.py
```

### Blender Addon

1. Open Blender
2. Go to Edit > Preferences > Add-ons
3. Click "Install..." and select the `addon/` folder
4. Enable "blender-mcp-ultra"

### MCP Server Configuration

Add to your MCP client config:

```json
{
  "mcpServers": {
    "blender": {
      "command": "python",
      "args": ["-m", "blender_mcp.server"],
      "env": {
        "BLENDER_HOST": "localhost",
        "BLENDER_PORT": "9876"
      }
    }
  }
}
```

## Tools

### Scene Management
- `scene.get_info()` - Get scene information
- `scene.create(name)` - Create new scene
- `scene.delete(name)` - Delete scene
- `scene.set_active(name)` - Set active scene
- `scene.render_settings()` - Get/set render settings

### Objects
- `object.create(type, name, location)` - Create objects
- `object.delete(name)` - Delete objects
- `object.select(name, type)` - Select objects
- `object.transform(name, location, rotation, scale)` - Transform
- `object.duplicate(name, new_name)` - Duplicate objects
- `object.join(names)` - Join objects
- `object.get_info(name)` - Get object info
- `object.list(type)` - List objects

### Materials
- `material.create(name, color, metallic, roughness)` - Create materials
- `material.delete(name)` - Delete materials
- `material.assign(object_name, material_name)` - Assign material
- `material.get_info(name)` - Get material info
- `material.list()` - List materials
- `material.update(name, color, metallic, roughness)` - Update material

### Lights
- `light.create(type, name, location, energy, color)` - Create lights
- `light.delete(name)` - Delete lights
- `light.three_point()` - Setup three-point lighting
- `light.update(name, energy, color, size)` - Update lights
- `light.list()` - List lights

### Modifiers
- `modifier.add(object_name, type)` - Add modifier
- `modifier.remove(object_name, modifier_name)` - Remove modifier
- `modifier.apply(object_name, modifier_name)` - Apply modifier
- `modifier.list(object_name)` - List modifiers
- `modifier.update(object_name, modifier_name, properties)` - Update modifier
- `modifier.types()` - List modifier types

### Animation
- `animation.keyframe_insert(object_name, property, frame)` - Insert keyframe
- `animation.keyframe_delete(object_name, property)` - Delete keyframe
- `animation.set_keyframe(object_name, property, frame, value)` - Set keyframe
- `animation.get_fcurves(object_name)` - Get F-curves
- `animation.set_interpolation(object_name, interpolation)` - Set interpolation
- `animation.play(start, end)` - Play animation
- `animation.stop()` - Stop animation
- `animation.clear(object_name)` - Clear animation

### Camera
- `camera.create(name, location, lens)` - Create camera
- `camera.delete(name)` - Delete camera
- `camera.set_active(name)` - Set active camera
- `camera.update(name, lens, dof)` - Update camera
- `camera.track_to(camera_name, target_name)` - Track object
- `camera.list()` - List cameras
- `camera.setResolution(width, height)` - Set resolution
- `camera.set_framing(camera_name, object_name)` - Set framing

### Render
- `render.render(filepath, engine)` - Render scene
- `render.viewport(filepath)` - Viewport screenshot
- `render.settings()` - Get/set render settings
- `render.set_engine(engine)` - Set render engine
- `render.set_output(filepath, format)` - Set output
- `render.set_cycles_settings(samples, denoising)` - Cycles settings
- `render.set_eevee_settings(samples, ssr, bloom)` - EEVEE settings
- `render.set_filmic(look, exposure, gamma)` - Color management

### I/O
- `io.export_fbx(filepath)` - Export FBX
- `io.export_obj(filepath)` - Export OBJ
- `io.export_gltf(filepath, format)` - Export glTF
- `io.export_stl(filepath)` - Export STL
- `io.import_fbx(filepath)` - Import FBX
- `io.import_obj(filepath)` - Import OBJ
- `io.import_gltf(filepath)` - Import glTF
- `io.import_stl(filepath)` - Import STL
- `io.save_file(filepath)` - Save file
- `io.load_file(filepath)` - Load file

### UV/Texture
- `uv.unwrap(method, margin)` - Unwrap UVs
- `uv.pack(margin)` - Pack UV islands
- `uv.smart_project(angle_limit)` - Smart UV project
- `uv.list(object_name)` - List UV maps
- `uv.create(object_name, name)` - Create UV map
- `uv.delete(object_name, name)` - Delete UV map
- `texture.create(name, width, height, color)` - Create texture
- `texture.list()` - List textures
- `texture.assign_to_material(material_name, texture_name)` - Assign texture
- `uv.bake(type, margin)` - Bake textures

### Rigging
- `rigging.create_armature(name, location)` - Create armature
- `rigging.add_bone(armature_name, name, head, tail)` - Add bone
- `rigging.add_constraint(object_name, type, target)` - Add constraint
- `rigging.create_vertex_group(object_name, name)` - Create vertex group
- `rigging.assign_vertex_group(object_name, group_name, weight)` - Assign weights
- `rigging.auto_weight(object_name, armature_name)` - Auto weight
- `rigging.list_bones(armature_name)` - List bones
- `rigging.apply_armature(object_name)` - Apply armature

### Batch
- `batch.rename(pattern, replace)` - Batch rename
- `batch.delete_by_type(type)` - Delete by type
- `batch.apply_transforms()` - Apply transforms
- `batch.add_modifier(object_names, modifier_type)` - Add modifier to multiple
- `batch.set_material(object_names, material_name)` - Set material for multiple
- `batch.turntable(object_name, frames, axis)` - Create turntable

### Scene Utils
- `scene_utils.cleanup()` - Clean scene
- `scene_utils.purge_orphans()` - Purge orphans
- `scene_utils.mesh_analysis(object_name)` - Analyze mesh
- `scene_utils.apply_all_transforms()` - Apply transforms
- `scene_utils.origin_to_geometry(object_name)` - Origin to geometry
- `scene_utils.fix_normals(object_name)` - Fix normals
- `scene_utils.remove_doubles(object_name, distance)` - Remove doubles
- `scene_utils.triangulate(object_name)` - Triangulate mesh

### Printing (3D)
- `printing.check_manifold(object_name)` - Check manifold
- `printing.check_watertight(object_name)` - Check watertight
- `printing.check_thinwalls(object_name, min_thickness)` - Check thin walls
- `printing.scale_to_mm(object_name, scale_factor)` - Scale to mm
- `printing.set_dimensions_mm(object_name, x, y, z)` - Set dimensions
- `printing.info(object_name)` - Get print info

### Shader Nodes
- `shader.add_node(material_name, node_type)` - Add shader node
- `shader.connect_nodes(material_name, from_node, from_socket, to_node, to_socket)` - Connect nodes
- `shader.set_node_value(material_name, node_name, input_name, value)` - Set node value
- `shader.delete_node(material_name, node_name)` - Delete node
- `shader.list_nodes(material_name)` - List nodes
- `shader.create_material_nodes(material_name, preset)` - Create preset
- `shader.group_nodes(material_name, node_names)` - Group nodes
- `shader.ungroup_nodes(material_name, group_name)` - Ungroup nodes

### Geometry Nodes
- `geonodes.add_modifier(object_name, node_group)` - Add GN modifier
- `geonodes.create_group(name)` - Create node group
- `geonodes.add_node(group_name, node_type)` - Add node
- `geonodes.connect(group_name, from_node, from_socket, to_node, to_socket)` - Connect nodes
- `geonodes.list_groups()` - List GN groups
- `geonodes.scatter(object_name, density, instance_name)` - Scatter setup
- `geonodes.array(object_name, count, offset_axis)` - Array setup
- `geonodes.delete_geometry(object_name, mode)` - Delete geometry

## Skills

19 specialized skills for Claude Code/Cursor:

1. **modeling** - Professional 3D modeling
2. **materials** - PBR materials
3. **lighting** - Studio lighting
4. **animation** - Professional animation
5. **camera** - Cinematography
6. **rendering** - Render optimization
7. **geometry_nodes** - Procedural systems
8. **rigging** - Character rigging
9. **compositing** - Post-processing
10. **io_export** - File export/import
11. **simulation** - Physics simulations
12. **texturing** - Texture creation
13. **scene_setup** - Scene organization
14. **procedural** - Parametric creation
15. **optimization** - Performance optimization
16. **workflow** - Professional workflows
17. **multi_dcc** - Multi-DCC pipelines
18. **video** - Video production
19. **production** - Production pipelines

## Security

- **AST Validation**: 200+ blocked patterns
- **Sandboxed Execution**: Isolated namespace with timeout
- **Rate Limiting**: Per-user token bucket algorithm
- **Audit Logging**: Structured JSON with file rotation
- **Input Validation**: SQL injection, XSS, path traversal prevention

## Architecture

```
blender-mcp-ultra/
├── src/
│   ├── core/           # Domain entities and interfaces
│   ├── adapters/       # Blender, LLM, Asset adapters
│   ├── infrastructure/ # Security, Network, Cache, Logging
│   ├── presentation/   # MCP Server, Addon, CLI
│   └── tools/          # 118 tools across 16 categories
├── skills/             # 19 skill definitions
├── tests/              # Unit and integration tests
└── docs/               # Documentation
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run unit tests only
pytest tests/unit/ -v

# Run integration tests (requires Blender running)
pytest tests/integration/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## License

MIT License

## Contributing

Contributions welcome! Please read CONTRIBUTING.md first.
