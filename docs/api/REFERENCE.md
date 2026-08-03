# API Reference — blender-mcp-ultra

Complete reference for all 215+ tools available via MCP.

## Table of Contents

- [Scene Tools](#scene-tools)
- [Object Tools](#object-tools)
- [Material Tools](#material-tools)
- [Light Tools](#light-tools)
- [Camera Tools](#camera-tools)
- [Modifier Tools](#modifier-tools)
- [Animation Tools](#animation-tools)
- [Render Tools](#render-tools)
- [I/O Tools](#io-tools)
- [UV/Texture Tools](#uvtexture-tools)
- [Rigging Tools](#rigging-tools)
- [Batch Tools](#batch-tools)
- [Scene Utils Tools](#scene-utils-tools)
- [Printing Tools](#printing-tools)
- [Shader Node Tools](#shader-node-tools)
- [Geometry Node Tools](#geometry-node-tools)

---

## Scene Tools

### `scene.get_info`
Get information about the current Blender scene.

**Parameters:** None

**Returns:**
```json
{
  "name": "Scene",
  "object_count": 5,
  "camera_count": 1,
  "light_count": 2,
  "objects": [...]
}
```

### `scene.render_settings`
Get or set render settings.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| engine | string | No | Render engine (CYCLES, BLENDER_EEVEE) |
| samples | int | No | Render samples |
| resolution_x | int | No | Resolution width |
| resolution_y | int | No | Resolution height |

---

## Object Tools

### `object.create`
Create a new object.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| type | string | Yes | Object type (MESH, CURVE, LIGHT, CAMERA) |
| name | string | No | Object name |
| location | tuple | No | Object location [x, y, z] |

**Returns:**
```json
{
  "success": true,
  "name": "Cube",
  "type": "MESH",
  "location": [0.0, 0.0, 0.0]
}
```

### `object.delete`
Delete an object.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| name | string | Yes | Object name |

### `object.list`
List all objects in the scene.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| type | string | No | Filter by object type |

### `object.get_info`
Get information about an object.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| name | string | Yes | Object name |

### `object.transform`
Transform an object.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| name | string | Yes | Object name |
| location | tuple | No | New location [x, y, z] |
| rotation | tuple | No | New rotation (Euler) [x, y, z] |
| scale | tuple | No | New scale [x, y, z] |

### `object.duplicate`
Duplicate an object.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| name | string | Yes | Object name |
| new_name | string | No | New object name |
| linked | bool | No | Create linked duplicate |

### `object.select`
Select objects.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| name | string | No | Object name |
| type | string | No | Object type filter |

---

## Material Tools

### `material.create`
Create a new material.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| name | string | Yes | Material name |
| color | tuple | No | Base color RGBA [r, g, b, a] |
| metallic | float | No | Metallic value (0-1) |
| roughness | float | No | Roughness value (0-1) |

**Returns:**
```json
{
  "success": true,
  "name": "RedMetal",
  "color": [1, 0, 0, 1],
  "metallic": 0.8,
  "roughness": 0.2
}
```

### `material.assign`
Assign material to object.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| object_name | string | Yes | Object name |
| material_name | string | Yes | Material name |

### `material.list`
List all materials.

**Parameters:** None

---

## Light Tools

### `light.create`
Create a new light.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| type | string | Yes | Light type (POINT, SUN, SPOT, AREA) |
| name | string | No | Light name |
| location | tuple | No | Light location [x, y, z] |
| energy | float | No | Light energy |
| color | tuple | No | Light color [r, g, b] |

### `light.three_point`
Setup three-point lighting.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| key_energy | float | No | Key light energy (default: 1000) |
| fill_energy | float | No | Fill light energy (default: 500) |
| rim_energy | float | No | Rim light energy (default: 800) |
| distance | float | No | Distance from center (default: 5) |

---

## Camera Tools

### `camera.create`
Create a camera.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| name | string | No | Camera name |
| location | tuple | No | Camera location [x, y, z] |
| lens | float | No | Focal length (default: 50) |

### `camera.setResolution`
Set render resolution.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| width | int | No | Resolution width |
| height | int | No | Resolution height |
| percentage | float | No | Resolution percentage |

---

## Modifier Tools

### `modifier.add`
Add a modifier to an object.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| object_name | string | Yes | Object name |
| type | string | Yes | Modifier type (SUBSURF, BEVEL, ARRAY, etc.) |

### `modifier.types`
List available modifier types.

**Parameters:** None

**Returns:**
```json
{
  "types": [
    {"id": "ARRAY", "name": "Array", "category": "Generate"},
    {"id": "BEVEL", "name": "Bevel", "category": "Generate"},
    ...
  ]
}
```

---

## Animation Tools

### `animation.set_keyframe`
Set a keyframe value.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| object_name | string | Yes | Object name |
| property | string | Yes | Property path (e.g., "location") |
| frame | int | Yes | Frame number |
| value | any | Yes | Keyframe value |

### `animation.get_fcurves`
Get F-curves for an object.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| object_name | string | Yes | Object name |

---

## Shader Node Tools

### `shader.add_node`
Add a shader node to a material.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| material_name | string | Yes | Material name |
| node_type | string | Yes | Node type (ShaderNodeTexNoise, etc.) |

### `shader.list_nodes`
List all nodes in a material.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| material_name | string | Yes | Material name |

---

## Geometry Node Tools

### `geonodes.create_group`
Create a geometry node group.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| name | string | Yes | Node group name |

### `geonodes.list_groups`
List all geometry node groups.

**Parameters:** None

### `geonodes.scatter`
Quick scatter setup on faces.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| object_name | string | Yes | Object name |
| density | float | No | Scatter density (default: 10) |
| instance_name | string | No | Instance object name |

---

## Error Handling

All tools return a consistent format:

**Success:**
```json
{
  "success": true,
  "data": {...}
}
```

**Error:**
```json
{
  "success": false,
  "error": "Error message"
}
```

**Common Errors:**
- `"Object not found: X"` — Object doesn't exist
- `"Material not found: X"` — Material doesn't exist
- `"No mesh object found"` — No mesh available
- `"Export needs GUI"` — Export requires GUI mode
