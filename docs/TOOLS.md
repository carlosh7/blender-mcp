<!-- GENERADO: scripts/gen_tools_docs.py — no editar a mano -->

# Referencia de tools (241)

Registry completo: 241 tools en 17 categorías. Generado desde `mcp_ultra/tools/` (la misma fuente que usa el gateway).

| Categoría | Tools |
|---|---|
| `animation` | `animation.clear`, `animation.constraint_add`, `animation.driver_add`, `animation.fcurve_info`, `animation.fcurve_set_key`, `animation.get_fcurves`, `animation.keyframe_delete`, `animation.keyframe_insert`, `animation.nla_track_add`, `animation.play`, `animation.set_interpolation`, `animation.set_keyframe`, `animation.shape_key_add`, `animation.shape_key_set`, `animation.stop` |
| `batch` | `batch.add_modifier`, `batch.apply_transforms`, `batch.delete_by_type`, `batch.rename`, `batch.set_material`, `batch.turntable` |
| `camera` | `camera.check`, `camera.create`, `camera.delete`, `camera.list`, `camera.setResolution`, `camera.set_active`, `camera.set_framing`, `camera.track_to`, `camera.update` |
| `geometry_nodes` | `geonodes.add_modifier`, `geonodes.add_node`, `geonodes.array`, `geonodes.connect`, `geonodes.create_group`, `geonodes.delete_geometry`, `geonodes.list_groups`, `geonodes.node_set_input`, `geonodes.scatter` |
| `guidance` | `guidance.get`, `guidance.list` |
| `io` | `asset.load`, `asset.save`, `asset.save_collection`, `asset.search`, `blueprint.categories`, `blueprint.get`, `blueprint.save`, `blueprint.search`, `export.batch`, `export.for_target`, `export.game_collision`, `export.lods`, `io.export_fbx`, `io.export_gltf`, `io.export_obj`, `io.export_stl`, `io.import_fbx`, `io.import_gltf`, `io.import_obj`, `io.import_stl`, `io.load_file`, `io.save_file` |
| `lights` | `light.create`, `light.delete`, `light.list`, `light.three_point`, `light.update`, `scene.mood` |
| `materials` | `material.assign`, `material.create`, `material.delete`, `material.get_info`, `material.list`, `material.pbr`, `material.update` |
| `modifiers` | `modifier.add`, `modifier.apply`, `modifier.list`, `modifier.remove`, `modifier.types`, `modifier.update`, `physics.bake`, `physics.free_cache` |
| `objects` | `curve.bezier_add`, `curve.set_point`, `grease_pencil.add`, `mesh.bevel_edges`, `mesh.delete_elements`, `mesh.extrude_faces`, `mesh.get_topology`, `mesh.inset_faces`, `mesh.merge_verts`, `mesh.move_verts`, `mesh.recalc_normals`, `mesh.select`, `mesh.smooth_verts`, `mesh.subdivide_faces`, `metaball.add`, `metaball.add_element`, `object.create`, `object.delete`, `object.duplicate`, `object.get_info`, `object.join`, `object.list`, `object.place_bottom`, `object.select`, `object.snap_to`, `object.transform`, `perf.auto_lod`, `physics.bake_cache`, `physics.bake_rigidbody`, `physics.cloth_add`, `physics.collision_add`, `physics.force_field_add`, `physics.particles_add`, `physics.preset`, `physics.rigidbody_add`, `physics.rigidbody_constraint`, `physics.soft_body_add`, `sculpt.base`, `sculpt.brush`, `sculpt.multires`, `sculpt.smooth`, `sculpt.voxel_remesh`, `text.add`, `text.set_body` |
| `printing` | `printing.check_manifold`, `printing.check_thinwalls`, `printing.check_watertight`, `printing.info`, `printing.scale_to_mm`, `printing.set_dimensions_mm` |
| `render` | `compositor.connect`, `compositor.list_nodes`, `compositor.node_add`, `compositor.node_set_input`, `inspect.turntable`, `inspect.view`, `perf.render_estimate`, `render.preview`, `render.render`, `render.set_cycles_settings`, `render.set_eevee_settings`, `render.set_engine`, `render.set_filmic`, `render.set_output`, `render.settings`, `render.viewport`, `vlm.analyze`, `vlm.capture`, `vlm.composition_check`, `vlm.lighting_check`, `vlm.quick_check` |
| `rigging` | `rigging.add_bone`, `rigging.add_constraint`, `rigging.apply_armature`, `rigging.assign_vertex_group`, `rigging.auto_weight`, `rigging.create_armature`, `rigging.create_vertex_group`, `rigging.list_bones` |
| `scene` | `scene.copy_object_to`, `scene.create`, `scene.delete`, `scene.get_info`, `scene.list_scenes`, `scene.preset`, `scene.query`, `scene.render_settings`, `scene.set_active` |
| `scene_utils` | `collab.broadcast`, `collab.lock_acquire`, `collab.lock_release`, `collab.lock_release_all`, `collab.locks_list`, `collab.message_get`, `collab.message_send`, `collab.task_assign`, `collab.task_complete`, `collab.task_pending`, `collab.task_register`, `collab.task_status`, `docs.export_json`, `docs.object`, `docs.scene`, `inspect.topology`, `perf.batch_optimize`, `perf.memory_report`, `perf.optimize_scene`, `perf.stats`, `plan.add_step`, `plan.create`, `plan.execute`, `plan.get`, `scene.check_blockout`, `scene.cleanup`, `scene.diff`, `scene.explain`, `scene.fix_blockout`, `scene.mark`, `scene_utils.apply_all_transforms`, `scene_utils.cleanup`, `scene_utils.fix_normals`, `scene_utils.mesh_analysis`, `scene_utils.origin_to_geometry`, `scene_utils.purge_orphans`, `scene_utils.ray_pick`, `scene_utils.redo`, `scene_utils.remove_doubles`, `scene_utils.triangulate`, `scene_utils.undo`, `spatial.check_move`, `spatial.dimensions`, `spatial.floorplan`, `spatial.place`, `spatial.query`, `spatial.stack`, `tools.search`, `vc.list`, `vc.restore`, `vc.snapshot` |
| `shader_nodes` | `shader.add_node`, `shader.connect_nodes`, `shader.create_material_nodes`, `shader.delete_node`, `shader.group_nodes`, `shader.list_nodes`, `shader.set_node_value`, `shader.ungroup_nodes` |
| `uv_texture` | `texture.assign_to_material`, `texture.create`, `texture.list`, `uv.bake`, `uv.create`, `uv.delete`, `uv.list`, `uv.pack`, `uv.smart_project`, `uv.unwrap` |

---

## animation

### `animation.clear`

Clear all animation data from an object

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str | ✅ |  |

Ejemplos:
- `animation.clear(object_name='Cube')`


### `animation.constraint_add`

Añadir constraint (Copy_Location, Track_To, Child_Of, ...) con props

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str | ✅ |  |
| `type` | str | ✅ |  |
| `target` | str |  |  |
| `props` | dict |  |  |


### `animation.driver_add`

Driver con expresión y variables {nombre: 'objeto@data_path'}

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str | ✅ |  |
| `data_path` | str | ✅ |  |
| `index` | int | ✅ |  |
| `expression` | str | ✅ |  |
| `driver_vars` | dict |  |  |


### `animation.fcurve_info`

Listar fcurves y keyframes de la acción del objeto

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str | ✅ |  |
| `data_path` | str |  |  |


### `animation.fcurve_set_key`

Keyframe en canal concreto (data_path + índice de array)

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str | ✅ |  |
| `data_path` | str | ✅ |  |
| `index` | int | ✅ |  |
| `frame` | float | ✅ |  |
| `value` | float | ✅ |  |
| `interpolation` | str |  |  |


### `animation.get_fcurves`

Get F-Curves for an object

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str | ✅ |  |

Ejemplos:
- `animation.get_fcurves(object_name='Cube')`


### `animation.keyframe_delete`

Delete keyframes for a property

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str | ✅ |  |
| `property` | str | ✅ |  |

Ejemplos:
- `animation.keyframe_delete(object_name='Cube', property='location')`


### `animation.keyframe_insert`

Insert a keyframe for an object property

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str | ✅ |  |
| `property` | str | ✅ |  |
| `frame` | int |  | `None` |

Ejemplos:
- `animation.keyframe_insert(object_name='Cube', property='location', frame=1)`


### `animation.nla_track_add`

Añadir track NLA con la acción actual como strip

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str | ✅ |  |
| `track_name` | str |  |  |


### `animation.play`

Play animation

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `start` | int |  | `None` |
| `end` | int |  | `None` |

Ejemplos:
- `animation.play()`
- `animation.play(start=1, end=100)`


### `animation.set_interpolation`

Set interpolation mode for F-Curves

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str | ✅ |  |
| `interpolation` | str | ✅ |  |

Ejemplos:
- `animation.set_interpolation(object_name='Cube', interpolation='BEZIER')`


### `animation.set_keyframe`

Set a keyframe value at a specific frame

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str | ✅ |  |
| `property` | str | ✅ |  |
| `frame` | int | ✅ |  |
| `value` | str | ✅ |  |

Ejemplos:
- `animation.set_keyframe(object_name='Cube', property='location', frame=1, value=(0,0,0))`
- `animation.set_keyframe(object_name='Cube', property='location', frame=50, value=(5,0,3))`


### `animation.shape_key_add`

Añadir shape key (crea Basis si falta)

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str | ✅ |  |
| `name` | str | ✅ |  |
| `from_mix` | bool |  |  |


### `animation.shape_key_set`

Valor y/o desplazamiento de vértices de una shape key

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str | ✅ |  |
| `name` | str | ✅ |  |
| `value` | float |  |  |
| `move_verts` | dict |  |  |


### `animation.stop`

Stop animation

Ejemplos:
- `animation.stop()`


## batch

### `batch.add_modifier`

Add modifier to multiple objects

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_names` | list | ✅ |  |
| `modifier_type` | str | ✅ |  |


### `batch.apply_transforms`

Apply transforms to all objects

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `type_filter` | str |  |  |


### `batch.delete_by_type`

Delete all objects of a type

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `type` | str | ✅ |  |


### `batch.rename`

Batch rename objects

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `pattern` | str |  |  |
| `replace` | str |  |  |
| `type_filter` | str |  |  |


### `batch.set_material`

Set material for multiple objects

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_names` | list | ✅ |  |
| `material_name` | str | ✅ |  |


### `batch.turntable`

Create turntable animation

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str |  |  |
| `frames` | int |  |  |
| `axis` | str |  |  |


## camera

### `camera.check`

Diagnóstico de cámara: activa, lens, qué objetos están en el frustum y a qué distancia

Ejemplos:
- `camera.check()`


### `camera.create`

Create a camera

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `name` | str |  |  |
| `location` | tuple |  | `(0, -5, 2)` |
| `lens` | float |  | `50` |


### `camera.delete`

Delete a camera

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `name` | str | ✅ |  |


### `camera.list`

List all cameras


### `camera.setResolution`

Set render resolution

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `width` | int |  |  |
| `height` | int |  |  |
| `percentage` | float |  |  |


### `camera.set_active`

Set active camera

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `name` | str | ✅ |  |


### `camera.set_framing`

Set camera framing (center object)

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `camera_name` | str |  |  |
| `object_name` | str |  |  |


### `camera.track_to`

Make camera track to object

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `camera_name` | str | ✅ |  |
| `target_name` | str | ✅ |  |


### `camera.update`

Update camera properties

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `name` | str | ✅ |  |
| `lens` | float |  |  |
| `dof` | float |  |  |
| `clip_start` | float |  |  |
| `clip_end` | float |  |  |


## geometry_nodes

### `geonodes.add_modifier`

Add Geometry Nodes modifier

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str |  |  |
| `node_group` | str |  |  |


### `geonodes.add_node`

Add a node to geometry node group

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `group_name` | str | ✅ |  |
| `node_type` | str | ✅ |  |


### `geonodes.array`

Quick array setup

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str |  |  |
| `count` | int |  |  |
| `offset_axis` | str |  |  |


### `geonodes.connect`

Connect nodes in geometry node group

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `group_name` | str | ✅ |  |
| `from_node` | str | ✅ |  |
| `from_socket` | str | ✅ |  |
| `to_node` | str | ✅ |  |
| `to_socket` | str | ✅ |  |


### `geonodes.create_group`

Create a new geometry node group

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `name` | str |  |  |


### `geonodes.delete_geometry`

Delete geometry by selection

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str |  |  |
| `mode` | str |  |  |


### `geonodes.list_groups`

List all geometry node groups


### `geonodes.node_set_input`

Fijar valor default de un input de nodo (sin link)

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `group_name` | str | ✅ |  |
| `node_name` | str | ✅ |  |
| `input_name` | str | ✅ |  |
| `value` | any | ✅ |  |


### `geonodes.scatter`

Quick scatter setup on faces

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str |  |  |
| `density` | float |  |  |
| `instance_name` | str |  |  |


## guidance

### `guidance.get`

Devuelve la guía completa de un tema. Temas: animation, camera, compositing, export, geometry-nodes, io-export, lighting, materials, modeling, multi-dcc, optimization, procedural, production, rendering, rigging, scene-setup, simulation, text-to-blender, texturing, video, wireframe-to-3d, workflow

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `topic` | str | ✅ |  |

Ejemplos:
- `guidance.get(topic='lighting')`
- `guidance.get(topic='scene-setup')`


### `guidance.list`

Lista las guías de workflow y técnica disponibles (animación, iluminación, render, pipeline de producción...). Léelas antes de empezar workflows complejos.

Ejemplos:
- `guidance.list()`


## io

### `asset.load`

Cargar un asset de la biblioteca

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `name` | str | ✅ |  |
| `location` | list |  |  |


### `asset.save`

Guardar objetos como asset reutilizable

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `name` | str | ✅ |  |
| `object_names` | list | ✅ |  |
| `description` | str |  |  |
| `tags` | list |  |  |


### `asset.save_collection`

Guardar una colección como asset

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `collection_name` | str | ✅ |  |
| `asset_name` | str |  |  |


### `asset.search`

Buscar assets por texto/tags

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `query` | str |  |  |
| `tags` | list |  |  |


### `blueprint.categories`

Listar categorías de blueprints


### `blueprint.get`

Obtener blueprint por nombre

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `name` | str | ✅ |  |


### `blueprint.save`

Guardar blueprint con anclas 27-pt (data: {name, objects:[...], dims})

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `data` | dict | ✅ |  |
| `category` | str | ✅ |  |
| `name` | str | ✅ |  |


### `blueprint.search`

Buscar blueprints por query

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `query` | str |  |  |


### `export.batch`

Export batch de la escena/selección a varios formatos

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `directory` | str | ✅ |  |
| `formats` | list |  |  |
| `selection_only` | bool |  |  |


### `export.for_target`

Export por destino: game/web/print/film

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `target` | str | ✅ |  |
| `filepath` | str | ✅ |  |
| `engine` | str |  |  |
| `fmt` | str |  |  |


### `export.game_collision`

Malla de colisión para game engine (unreal/unity/godot)

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str | ✅ |  |
| `engine` | str |  |  |


### `export.lods`

Generar niveles de LOD para un objeto

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str | ✅ |  |
| `ratios` | list |  |  |


### `io.export_fbx`

Export scene to FBX

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `filepath` | str | ✅ |  |
| `use_selection` | bool |  |  |


### `io.export_gltf`

Export scene to glTF/GLB

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `filepath` | str | ✅ |  |
| `format` | str |  |  |


### `io.export_obj`

Export scene to OBJ

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `filepath` | str | ✅ |  |
| `use_selection` | bool |  |  |


### `io.export_stl`

Export scene to STL

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `filepath` | str | ✅ |  |
| `use_selection` | bool |  |  |


### `io.import_fbx`

Import FBX file

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `filepath` | str | ✅ |  |


### `io.import_gltf`

Import glTF file

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `filepath` | str | ✅ |  |


### `io.import_obj`

Import OBJ file

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `filepath` | str | ✅ |  |


### `io.import_stl`

Import STL file

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `filepath` | str | ✅ |  |


### `io.load_file`

Load blend file

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `filepath` | str | ✅ |  |


### `io.save_file`

Save blend file

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `filepath` | str |  |  |


## lights

### `light.create`

Create a new light

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `type` | str | ✅ |  |
| `name` | str |  | `None` |
| `location` | tuple |  | `(0, 0, 5)` |
| `energy` | float |  | `1000.0` |
| `color` | tuple |  | `(1, 1, 1)` |

Ejemplos:
- `light.create(type='POINT', name='KeyLight', location=(3, -3, 5))`
- `light.create(type='SUN', energy=5, color=(1, 0.95, 0.9))`


### `light.delete`

Delete a light

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `name` | str | ✅ |  |

Ejemplos:
- `light.delete(name='KeyLight')`


### `light.list`

List all lights in the scene

Ejemplos:
- `light.list()`


### `light.three_point`

Setup three-point lighting

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `key_energy` | float |  | `1000` |
| `fill_energy` | float |  | `500` |
| `rim_energy` | float |  | `800` |
| `distance` | float |  | `5` |

Ejemplos:
- `light.three_point()`
- `light.three_point(key_energy=2000, distance=10)`


### `light.update`

Update light properties

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `name` | str | ✅ |  |
| `energy` | float |  | `None` |
| `color` | tuple |  | `None` |
| `size` | float |  | `None` |

Ejemplos:
- `light.update(name='KeyLight', energy=2000, color=(1, 0.9, 0.8))`


### `scene.mood`

Aplica un mood de iluminación (reemplaza luces y mundo, sin tocar geometría). Moods: cinematic, cyberpunk, fantasy, horror, minimal, warm_sunset

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `mood` | str | ✅ |  |

Ejemplos:
- `scene.mood(mood='cinematic')`


## materials

### `material.assign`

Assign material to object

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str | ✅ |  |
| `material_name` | str | ✅ |  |

Ejemplos:
- `material.assign(object_name='Cube', material_name='RedMetal')`


### `material.create`

Create a new material

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `name` | str | ✅ |  |
| `color` | tuple |  | `(0.8, 0.8, 0.8, 1.0)` |
| `metallic` | float |  | `0.0` |
| `roughness` | float |  | `0.5` |

Ejemplos:
- `material.create(name='RedMetal', color=(1, 0, 0, 1), metallic=0.8)`


### `material.delete`

Delete a material

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `name` | str | ✅ |  |

Ejemplos:
- `material.delete(name='RedMetal')`


### `material.get_info`

Get information about a material

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `name` | str | ✅ |  |

Ejemplos:
- `material.get_info(name='RedMetal')`


### `material.list`

List all materials in the scene

Ejemplos:
- `material.list()`


### `material.pbr`

Material PBR procedural: wood/fabric/metal/leather/stone/glass/ceramic/plastic/rubber

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `kind` | str | ✅ |  |
| `name` | str | ✅ |  |
| `color` | list |  |  |


### `material.update`

Update material properties

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `name` | str | ✅ |  |
| `color` | tuple |  | `None` |
| `metallic` | float |  | `None` |
| `roughness` | float |  | `None` |

Ejemplos:
- `material.update(name='RedMetal', roughness=0.2)`


## modifiers

### `modifier.add`

Add a modifier to an object

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str | ✅ |  |
| `type` | str | ✅ |  |
| `name` | str |  | `None` |

Ejemplos:
- `modifier.add(object_name='Cube', type='SUBSURF')`
- `modifier.add(object_name='Cube', type='BEVEL', name='MyBevel')`


### `modifier.apply`

Apply a modifier

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str | ✅ |  |
| `modifier_name` | str | ✅ |  |

Ejemplos:
- `modifier.apply(object_name='Cube', modifier_name='Subsurf')`


### `modifier.list`

List modifiers on an object

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str | ✅ |  |

Ejemplos:
- `modifier.list(object_name='Cube')`


### `modifier.remove`

Remove a modifier from an object

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str | ✅ |  |
| `modifier_name` | str | ✅ |  |

Ejemplos:
- `modifier.remove(object_name='Cube', modifier_name='MyBevel')`


### `modifier.types`

List available modifier types

Ejemplos:
- `modifier.types()`


### `modifier.update`

Update modifier properties

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str | ✅ |  |
| `modifier_name` | str | ✅ |  |
| `properties` | dict | ✅ |  |

Ejemplos:
- `modifier.update(object_name='Cube', modifier_name='Subsurf', properties={'levels': 3})`


### `physics.bake`

Hornea la simulación rigid body (linkea colección RBW y hornea la caché)

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `frame_start` | int |  | `1` |
| `frame_end` | int |  | `50` |

Ejemplos:
- `physics.bake(frame_end=60)`


### `physics.free_cache`

Invalida la caché de simulación (obligatorio tras cambiar keyframes)

Ejemplos:
- `physics.free_cache()`


## objects

### `curve.bezier_add`

Curva Bézier 3D por puntos; bevel_depth > 0 la vuelve tubo

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `name` | str |  |  |
| `points` | list |  |  |
| `closed` | bool |  |  |
| `bevel_depth` | float |  |  |


### `curve.set_point`

Mover punto de control de Bézier

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str | ✅ |  |
| `index` | int | ✅ |  |
| `co` | list | ✅ |  |
| `handle` | str |  |  |


### `grease_pencil.add`

Objeto Grease Pencil vacío con una capa

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `name` | str |  |  |


### `mesh.bevel_edges`

Biselar aristas concretas

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str | ✅ |  |
| `edge_indices` | list | ✅ |  |
| `width` | float |  |  |
| `segments` | int |  |  |


### `mesh.delete_elements`

Borrar caras/aristas/vértices por índice

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str | ✅ |  |
| `face_indices` | list |  |  |
| `edge_indices` | list |  |  |
| `vert_indices` | list |  |  |


### `mesh.extrude_faces`

Extruir caras a lo largo de su normal media

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str | ✅ |  |
| `face_indices` | list | ✅ |  |
| `thickness` | float |  |  |


### `mesh.get_topology`

Topología del mesh: conteos + caras (índice, centro, normal, vértices)

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str | ✅ |  |
| `include_faces` | bool |  |  |
| `max_faces` | int |  |  |


### `mesh.inset_faces`

Inset en caras (mismo plano) con profundidad opcional

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str | ✅ |  |
| `face_indices` | list | ✅ |  |
| `thickness` | float |  |  |
| `depth` | float |  |  |


### `mesh.merge_verts`

Fusionar vértices cercanos (remove doubles) en una selección

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str | ✅ |  |
| `vert_indices` | list | ✅ |  |
| `dist` | float |  |  |


### `mesh.move_verts`

Mover vértices por offset o a posiciones absolutas

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str | ✅ |  |
| `vert_indices` | list |  |  |
| `offset` | list |  |  |
| `positions` | dict |  |  |


### `mesh.recalc_normals`

Recalcular normales hacia fuera

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str | ✅ |  |


### `mesh.select`

Valida y devuelve los componentes seleccionables por índice

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str | ✅ |  |
| `face_indices` | list |  |  |
| `edge_indices` | list |  |  |
| `vert_indices` | list |  |  |


### `mesh.smooth_verts`

Suavizar posiciones de vértices (Laplaciano simple)

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str | ✅ |  |
| `iterations` | int |  |  |
| `face_indices` | list |  |  |


### `mesh.subdivide_faces`

Subdividir caras (o todo el mesh si no se dan índices)

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str | ✅ |  |
| `face_indices` | list |  |  |
| `cuts` | int |  |  |


### `metaball.add`

Metaball (se fusiona con otras del mismo nombre-base)

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `name` | str |  |  |
| `location` | list |  |  |
| `radius` | float |  |  |
| `stiffness` | float |  |  |


### `metaball.add_element`

Elemento adicional en una metaball (fusión orgánica)

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str | ✅ |  |
| `location` | list | ✅ |  |
| `radius` | float |  |  |


### `object.create`

Create a new object

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `type` | str | ✅ |  |
| `name` | str |  | `None` |
| `location` | tuple |  | `(0, 0, 0)` |

Ejemplos:
- `object.create(type='MESH', name='Cube')`
- `object.create(type='LIGHT', name='Sun', location=(0, 0, 5))`


### `object.delete`

Delete an object

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `name` | str | ✅ |  |

Ejemplos:
- `object.delete(name='Cube')`


### `object.duplicate`

Duplicate an object

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `name` | str | ✅ |  |
| `new_name` | str |  | `None` |
| `linked` | bool |  | `False` |

Ejemplos:
- `object.duplicate(name='Cube')`
- `object.duplicate(name='Cube', new_name='Cube.001', linked=True)`


### `object.get_info`

Get information about an object

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `name` | str | ✅ |  |

Ejemplos:
- `object.get_info(name='Cube')`


### `object.join`

Join multiple objects

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `names` | list | ✅ |  |

Ejemplos:
- `object.join(names=['Cube', 'Cube.001', 'Cube.002'])`


### `object.list`

List all objects in the scene

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `type` | str |  | `None` |

Ejemplos:
- `object.list()`
- `object.list(type='MESH')`


### `object.place_bottom`

Coloca el punto más bajo del bbox del objeto en (x,y,z) — inmune a offsets de origen y escala

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `name` | str | ✅ |  |
| `x` | float |  | `0.0` |
| `y` | float |  | `0.0` |
| `z` | float |  | `0.0` |

Ejemplos:
- `object.place_bottom(name='Mug', z=0.75)`


### `object.select`

Select objects

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `name` | str |  | `None` |
| `type` | str |  | `None` |
| `all` | bool |  | `False` |

Ejemplos:
- `object.select(name='Cube')`
- `object.select(type='MESH')`
- `object.select(all=True)`


### `object.snap_to`

Coloca un objeto en relación bbox-aware con otro (on_top/beside_x/beside_y/behind/front)

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `name` | str | ✅ |  |
| `target` | str | ✅ |  |
| `relation` | str |  | `on_top` |
| `gap` | float |  | `0.0` |

Ejemplos:
- `object.snap_to(name='Mug', target='Mesa', relation='on_top')`


### `object.transform`

Transform an object (move, rotate, scale)

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `name` | str | ✅ |  |
| `location` | tuple |  | `None` |
| `rotation` | tuple |  | `None` |
| `scale` | tuple |  | `None` |

Ejemplos:
- `object.transform(name='Cube', location=(1, 2, 3))`
- `object.transform(name='Cube', rotation=(0, 0, 1.57))`
- `object.transform(name='Cube', scale=(2, 2, 2))`


### `perf.auto_lod`

LOD automático por distancia

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str | ✅ |  |
| `distance_threshold` | float |  |  |


### `physics.bake_cache`

Cocinar todas las cachés de física

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `frame_start` | int |  |  |
| `frame_end` | int |  |  |


### `physics.bake_rigidbody`

Cocinar rigid body world hasta N frames

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `frames` | int |  |  |


### `physics.cloth_add`

Simulación de tela

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str | ✅ |  |
| `quality` | int |  |  |
| `mass` | float |  |  |


### `physics.collision_add`

Modifier de colisión con rebote

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str | ✅ |  |
| `bounce` | float |  |  |


### `physics.force_field_add`

Force field (WIND, FORCE, TURBULENCE, VORTEX...)

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `kind` | str |  |  |
| `location` | list |  |  |
| `strength` | float |  |  |
| `name` | str |  |  |


### `physics.particles_add`

Sistema de partículas por preset (snow/rain/sparks...)

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str | ✅ |  |
| `preset` | str |  |  |


### `physics.preset`

Preset físico completo del addon sobre un objeto

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str | ✅ |  |
| `preset_name` | str | ✅ |  |


### `physics.rigidbody_add`

Rigid body (ACTIVE cae / PASSIVE obstáculo) con masa y fricción

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str | ✅ |  |
| `body_type` | str |  |  |
| `mass` | float |  |  |
| `friction` | float |  |  |
| `restitution` | float |  |  |


### `physics.rigidbody_constraint`

Constraint entre dos rigid bodies (HINGE/SLIDER/FIXED...)

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_a` | str | ✅ |  |
| `object_b` | str | ✅ |  |
| `constraint_type` | str |  |  |
| `location` | list |  |  |


### `physics.soft_body_add`

Soft body por preset

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str | ✅ |  |
| `preset` | str |  |  |


### `sculpt.base`

Base de escultura (sphere/cube) con densidad preparada

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `primitive_type` | str |  |  |
| `subdivisions` | int |  |  |


### `sculpt.brush`

Pincel de esculpido activo (nombre, fuerza, radio)

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `brush_name` | str | ✅ |  |
| `strength` | float |  |  |
| `radius` | float |  |  |


### `sculpt.multires`

Multiresolution subdivide

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str | ✅ |  |
| `levels` | int |  |  |


### `sculpt.smooth`

Suavizado completo de la malla

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str | ✅ |  |
| `iterations` | int |  |  |


### `sculpt.voxel_remesh`

Voxel remesh para esculpido

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str | ✅ |  |
| `voxel_size` | float |  |  |


### `text.add`

Texto 3D extruible/biselable

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `name` | str |  |  |
| `body` | str |  |  |
| `size` | float |  |  |
| `extrude` | float |  |  |
| `bevel_depth` | float |  |  |
| `align` | str |  |  |


### `text.set_body`

Cambiar el texto de un objeto FONT

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str | ✅ |  |
| `body` | str | ✅ |  |


## printing

### `printing.check_manifold`

Check if mesh is manifold

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str |  |  |


### `printing.check_thinwalls`

Check for thin walls

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str |  |  |
| `min_thickness` | float |  |  |


### `printing.check_watertight`

Check if mesh is watertight

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str |  |  |


### `printing.info`

Get 3D print info (volume, area, dimensions)

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str |  |  |


### `printing.scale_to_mm`

Scale object to millimeters

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str |  |  |
| `scale_factor` | float |  |  |


### `printing.set_dimensions_mm`

Set object dimensions in mm

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str |  |  |
| `x` | float |  |  |
| `y` | float |  |  |
| `z` | float |  |  |


## render

### `compositor.connect`

Enlazar output→input entre nodos

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `from_node` | str | ✅ |  |
| `from_socket` | str |  |  |
| `to_node` | str | ✅ |  |
| `to_socket` | str |  |  |


### `compositor.list_nodes`

Listar nodos del compositor con inputs/outputs


### `compositor.node_add`

Añadir nodo de composición por bl_idname (activa use_nodes)

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `node_type` | str | ✅ |  |
| `location` | list |  |  |


### `compositor.node_set_input`

Fijar valor de input o enlazar desde otro nodo (link_from='Nodo.Output')

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `node_name` | str | ✅ |  |
| `input_name` | str | ✅ |  |
| `value` | any |  |  |
| `link_from` | str |  |  |


### `inspect.turntable`

Órbita automática: N renders equidistantes alrededor del objeto

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `name` | str | ✅ |  |
| `frames` | int |  | `6` |

Ejemplos:
- `inspect.turntable(name='Mug', frames=8)`


### `inspect.view`

Render de inspección determinístico: silhouette (forma), wireframe (densidad), uv_checker (despliegue) o normals (orientación). No requiere VLM

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `name` | str | ✅ |  |
| `mode` | str |  | `silhouette` |
| `filepath` | str |  |  |

Ejemplos:
- `inspect.view(name='Mug', mode='silhouette')`
- `inspect.view(name='Mug', mode='uv_checker')`


### `perf.render_estimate`

Estimación de tiempo de render


### `render.preview`

Render borrador rápido (EEVEE, resolución reducida) para validar encuadre sin esperar Cycles

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `filepath` | str |  |  |
| `samples` | int |  | `16` |
| `scale` | int |  | `50` |

Ejemplos:
- `render.preview()`


### `render.render`

Render current scene

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `filepath` | str |  |  |
| `engine` | str |  |  |


### `render.set_cycles_settings`

Set Cycles render settings

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `samples` | int |  |  |
| `denoising` | bool |  |  |
| `max_bounces` | int |  |  |
| `use_gpu` | bool |  |  |


### `render.set_eevee_settings`

Set EEVEE render settings

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `taa_render_samples` | int |  |  |
| `use_ssr` | bool |  |  |
| `use_bloom` | bool |  |  |


### `render.set_engine`

Set render engine

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `engine` | str | ✅ |  |


### `render.set_filmic`

Set Filmic color management

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `look` | str |  |  |
| `exposure` | float |  |  |
| `gamma` | float |  |  |


### `render.set_output`

Set render output path and format

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `filepath` | str |  |  |
| `format` | str |  |  |


### `render.settings`

Get/set render settings

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `engine` | str |  |  |
| `samples` | int |  |  |
| `resolution_x` | int |  |  |
| `resolution_y` | int |  |  |
| `denoising` | bool |  |  |


### `render.viewport`

Render viewport screenshot

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `filepath` | str |  |  |


### `vlm.analyze`

Analizar imagen con VLM (ollama/openai/claude) según un prompt

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `image_path` | str | ✅ |  |
| `prompt` | str | ✅ |  |
| `provider` | str |  |  |


### `vlm.capture`

Captura visual actual (viewport en GUI, render EEVEE rápido en headless)

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `filepath` | str |  |  |
| `resolution` | int |  |  |


### `vlm.composition_check`

Análisis de composición

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `provider` | str |  |  |


### `vlm.lighting_check`

Análisis de iluminación

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `provider` | str |  |  |


### `vlm.quick_check`

Chequeo visual rápido de la escena (captura + análisis)

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `provider` | str |  |  |


## rigging

### `rigging.add_bone`

Add a bone to armature

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `armature_name` | str | ✅ |  |
| `name` | str |  |  |
| `head` | tuple |  |  |
| `tail` | tuple |  |  |


### `rigging.add_constraint`

Add constraint to bone

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str | ✅ |  |
| `type` | str | ✅ |  |
| `target` | str |  |  |


### `rigging.apply_armature`

Apply armature modifier

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str | ✅ |  |


### `rigging.assign_vertex_group`

Assign vertices to group

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str | ✅ |  |
| `group_name` | str | ✅ |  |
| `weight` | float |  |  |


### `rigging.auto_weight`

Automatic weight painting

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str |  |  |
| `armature_name` | str |  |  |


### `rigging.create_armature`

Create an armature

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `name` | str |  |  |
| `location` | tuple |  |  |


### `rigging.create_vertex_group`

Create vertex group

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str | ✅ |  |
| `name` | str |  |  |


### `rigging.list_bones`

List bones in armature

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `armature_name` | str | ✅ |  |


## scene

### `scene.copy_object_to`

Copiar o linkear un objeto a otra escena

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str | ✅ |  |
| `target_scene` | str | ✅ |  |
| `link` | bool |  |  |


### `scene.create`

Create a new scene

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `name` | str | ✅ |  |

Ejemplos:
- `scene.create(name='MyScene')`


### `scene.delete`

Delete a scene

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `name` | str | ✅ |  |

Ejemplos:
- `scene.delete(name='MyScene')`


### `scene.get_info`

Get information about the current scene

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `include_objects` | bool |  | `True` |
| `include_materials` | bool |  | `False` |

Ejemplos:
- `scene.get_info()`
- `scene.get_info(include_objects=True, include_materials=True)`


### `scene.list_scenes`

Listar escenas con conteos e indicar la activa

Ejemplos:
- `scene.list_scenes()`


### `scene.preset`

Crea el entorno base de un preset (luces+entorno+suelo). Presets: bosque, cocina, cyberpunk, desierto, estudio, exterior, galeria, noche, oficina, sala

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `name` | str | ✅ |  |
| `keep_objects` | bool |  | `False` |

Ejemplos:
- `scene.preset(name='estudio')`
- `scene.preset(name='cyberpunk', keep_objects=True)`


### `scene.query`

Buscar objetos por nombre/tipo/distancia (el grep de la escena)

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `name_contains` | str |  |  |
| `name_regex` | str |  |  |
| `obj_type` | str |  |  |
| `near` | list |  |  |
| `max_distance` | float |  |  |
| `limit` | int |  |  |

Ejemplos:
- `scene.query(name_contains='Cube')`


### `scene.render_settings`

Get or set render settings

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `engine` | str |  | `None` |
| `samples` | int |  | `None` |
| `resolution_x` | int |  | `None` |
| `resolution_y` | int |  | `None` |

Ejemplos:
- `scene.render_settings()`
- `scene.render_settings(engine='CYCLES', samples=128)`


### `scene.set_active`

Set the active scene

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `name` | str | ✅ |  |

Ejemplos:
- `scene.set_active(name='MyScene')`


## scene_utils

### `collab.broadcast`

Broadcast a todos los agentes

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `sender_id` | str | ✅ |  |
| `message_type` | str |  |  |
| `content` | str |  |  |


### `collab.lock_acquire`

Lock por recurso/objeto para un agente (multi-agente fino)

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `agent_id` | str | ✅ |  |
| `resource` | str | ✅ |  |
| `timeout` | float |  |  |


### `collab.lock_release`

Liberar lock de un recurso

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `agent_id` | str | ✅ |  |
| `resource` | str | ✅ |  |


### `collab.lock_release_all`

Liberar todos los locks de un agente

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `agent_id` | str | ✅ |  |


### `collab.locks_list`

Listar locks activos


### `collab.message_get`

Bandeja de un agente

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `agent_id` | str | ✅ |  |
| `unread_only` | bool |  |  |


### `collab.message_send`

Mensaje directo entre agentes

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `sender_id` | str | ✅ |  |
| `receiver_id` | str | ✅ |  |
| `message_type` | str |  |  |
| `content` | str |  |  |


### `collab.task_assign`

Asignar tarea a un agente

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `task_id` | str | ✅ |  |
| `agent_id` | str | ✅ |  |


### `collab.task_complete`

Marcar tarea completada

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `task_id` | str | ✅ |  |
| `result` | str |  |  |


### `collab.task_pending`

Tareas pendientes (de un agente o todas)

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `agent_id` | str |  |  |


### `collab.task_register`

Registrar tarea en el tablero

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `task_id` | str | ✅ |  |
| `description` | str | ✅ |  |
| `assigned_to` | str |  |  |


### `collab.task_status`

Estado global del tablero


### `docs.export_json`

Exportar documentación de escena a JSON

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `filepath` | str |  |  |


### `docs.object`

Spec de documentación de un objeto

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str | ✅ |  |


### `docs.scene`

Documentación completa de la escena


### `inspect.topology`

Salud de topología: tris/quads/ngons, poles, UV, escala, densidad y score 0-100

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `name` | str | ✅ |  |

Ejemplos:
- `inspect.topology(name='Mug')`


### `perf.batch_optimize`

Optimizar toda la escena a un presupuesto de caras

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `target_faces` | int |  |  |


### `perf.memory_report`

Informe de uso de memoria


### `perf.optimize_scene`

Optimización automática de la escena


### `perf.stats`

Estadísticas de rendimiento


### `plan.add_step`

Añadir paso al plan (tipo, posición, parent/anchor/material)

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_type` | str | ✅ |  |
| `position` | list | ✅ |  |
| `parent` | str |  |  |
| `anchor` | str |  |  |
| `collection` | str |  |  |
| `material` | str |  |  |


### `plan.create`

Crear plan de construcción de escena

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `name` | str | ✅ |  |
| `description` | str |  |  |


### `plan.execute`

Ejecutar el plan en orden calculado


### `plan.get`

Ver el plan actual


### `scene.check_blockout`

Detecta blockout (primitivas sin detalle) en un objeto o toda la escena

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str |  |  |


### `scene.cleanup`

Detecta/elimina basura: duplicados .001, empties de test, meshes vacíos, escala no aplicada, huérfanos

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `dry_run` | bool |  | `True` |
| `purge_orphans` | bool |  | `True` |

Ejemplos:
- `scene.cleanup(dry_run=True)`
- `scene.cleanup(dry_run=False)`


### `scene.diff`

Qué cambió desde el último scene.mark (añadidos/eliminados/modificados)

Ejemplos:
- `scene.diff()`


### `scene.explain`

Explica un objeto en detalle: geometría, bbox, materiales (con resumen del árbol de nodos), modifiers, física y jerarquía

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `target` | str | ✅ |  |

Ejemplos:
- `scene.explain(target='Mug')`


### `scene.fix_blockout`

Autocorrección anti-blockout (bisel, suavizado, material)

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str | ✅ |  |


### `scene.mark`

Marca el estado actual de la escena para comparar luego con scene.diff

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `label` | str |  |  |

Ejemplos:
- `scene.mark(label='antes de la física')`


### `scene_utils.apply_all_transforms`

Apply all transforms


### `scene_utils.cleanup`

Clean up scene (orphans, unused)


### `scene_utils.fix_normals`

Recalculate normals

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str |  |  |


### `scene_utils.mesh_analysis`

Analyze mesh for issues

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str |  |  |


### `scene_utils.origin_to_geometry`

Set origin to geometry center

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str |  |  |


### `scene_utils.purge_orphans`

Purge orphan data blocks


### `scene_utils.ray_pick`

Raycast 3D: primer objeto tocado desde origen en dirección dada

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `origin` | list | ✅ |  |
| `direction` | list | ✅ |  |


### `scene_utils.redo`

Rehacer N pasos

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `steps` | int |  |  |


### `scene_utils.remove_doubles`

Remove duplicate vertices

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str |  |  |
| `distance` | float |  |  |


### `scene_utils.triangulate`

Triangulate mesh

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str |  |  |


### `scene_utils.undo`

Deshacer N pasos del stack de undo de Blender

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `steps` | int |  |  |


### `spatial.check_move`

¿Cuánto puede moverse un objeto en una dirección sin colisionar? No mueve nada

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `name` | str | ✅ |  |
| `direction` | str |  | `+x` |
| `distance` | float |  | `1.0` |

Ejemplos:
- `spatial.check_move(name='Silla', direction='+x', distance=2)`


### `spatial.dimensions`

Dimensiones reales (ancho×profundo×alto m) de 60 objetos comunes para dimensionar escenas creíbles

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `search` | str |  |  |

Ejemplos:
- `spatial.dimensions(search='mesa')`


### `spatial.floorplan`

Plano ASCII de la escena (top/front/right) para que el agente 'vea' la distribución sin render

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `view` | str |  | `top` |
| `cells` | int |  | `40` |

Ejemplos:
- `spatial.floorplan(view='top', cells=50)`


### `spatial.place`

Coloca un objeto respecto a otro con semántica (on_top/beside_x/beside_y/behind/front/on_floor) y chequeo de colisión

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `name` | str | ✅ |  |
| `relation` | str |  | `on_top` |
| `target` | str |  |  |
| `offset` | float |  | `0.0` |
| `check_collision` | bool |  | `True` |

Ejemplos:
- `spatial.place(name='Mug', relation='on_top', target='Mesa')`


### `spatial.query`

Query espacial: qué hay SOBRE un objeto (on=), qué está CERCA (near=, radius=) o listar por nombre

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `on` | str |  |  |
| `near` | str |  |  |
| `radius` | float |  | `1.0` |
| `name_contains` | str |  |  |
| `type_filter` | str |  | `MESH` |

Ejemplos:
- `spatial.query(on='Mesa')`
- `spatial.query(near='Puerta', radius=1.5)`


### `spatial.stack`

Apila objetos en orden (base primero) con centrado y gap

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `names` | str | ✅ |  |
| `gap` | float |  | `0.0` |

Ejemplos:
- `spatial.stack(names='Mesa,Tablero,Taza')`


### `tools.search`

Busca tools del registry por texto/categoría sin cargar las 223 definiciones. Ahorra contexto: úsalo antes de adivinar nombres

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `query` | str |  |  |
| `category` | str |  |  |
| `limit` | int |  | `15` |

Ejemplos:
- `tools.search(query='bevel')`
- `tools.search(category='render')`


### `vc.list`

Listar versiones guardadas


### `vc.restore`

Restaurar versión del historial

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `version_id` | str | ✅ |  |


### `vc.snapshot`

Snapshot versionado (historial persistente)

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `label` | str |  |  |


## shader_nodes

### `shader.add_node`

Add a shader node

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `material_name` | str | ✅ |  |
| `node_type` | str | ✅ |  |
| `location` | tuple |  |  |


### `shader.connect_nodes`

Connect two nodes

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `material_name` | str | ✅ |  |
| `from_node` | str | ✅ |  |
| `from_socket` | str | ✅ |  |
| `to_node` | str | ✅ |  |
| `to_socket` | str | ✅ |  |


### `shader.create_material_nodes`

Create common material setups

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `material_name` | str | ✅ |  |
| `preset` | str | ✅ |  |


### `shader.delete_node`

Delete a shader node

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `material_name` | str | ✅ |  |
| `node_name` | str | ✅ |  |


### `shader.group_nodes`

Group selected nodes

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `material_name` | str | ✅ |  |
| `node_names` | list | ✅ |  |
| `group_name` | str |  |  |


### `shader.list_nodes`

List all nodes in material

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `material_name` | str | ✅ |  |


### `shader.set_node_value`

Set a node input value

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `material_name` | str | ✅ |  |
| `node_name` | str | ✅ |  |
| `input_name` | str | ✅ |  |
| `value` | str | ✅ |  |


### `shader.ungroup_nodes`

Ungroup a node group

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `material_name` | str | ✅ |  |
| `group_name` | str | ✅ |  |


## uv_texture

### `texture.assign_to_material`

Assign texture to material

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `material_name` | str |  |  |
| `texture_name` | str |  |  |
| `slot` | str |  |  |


### `texture.create`

Create image texture

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `name` | str |  |  |
| `width` | int |  |  |
| `height` | int |  |  |
| `color` | tuple |  |  |


### `texture.list`

List all textures


### `uv.bake`

Bake textures

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `type` | str |  |  |
| `margin` | int |  |  |


### `uv.create`

Create UV map

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str |  |  |
| `name` | str |  |  |


### `uv.delete`

Delete UV map

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str |  |  |
| `name` | str |  |  |


### `uv.list`

List UV maps

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `object_name` | str |  |  |


### `uv.pack`

Pack UV islands

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `margin` | float |  |  |


### `uv.smart_project`

Smart UV project

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `angle_limit` | float |  |  |


### `uv.unwrap`

Unwrap UVs

| Parámetro | Tipo | Req | Default |
|---|---|---|---|
| `method` | str |  |  |
| `margin` | float |  |  |

