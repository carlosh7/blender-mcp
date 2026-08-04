# Changelog

All notable changes to blender-mcp-ultra will be documented in this file.

## [Unreleased]

### Added — permukaan v2.0 (128 → 138 tool)
- Command registry `addon/handlers.py` + fallback di `_axsock`;
  semua tool MCP dihasilkan dari satu spec `mcp_tools.py` (FastMCP + stdio_bridge)
- **Modeling**: 12 primitive data-API (aman di `blender -b`), boolean, 18 jenis
  modifier, bevel/extrude/inset bmesh, merge, join, kurva, teks 3D, screw/lathe,
  `create_empty`, `subdivide_mesh`, `loop_cut` (bisect_plane)
- **Coloring**: material PBR (Principled BSDF), graf node shader, image texture,
  vertex color per loop, emisi, transparansi, `colorize_from_scratch`
- **Rigging**: armature + bone + bone collection (4.0+), vertex group/weight,
  20 constraint, IK chain, `add_armature_modifier`, auto-rig, pose reset
- **Animation**: keyframe, animasi loc/rot/scale, action, interpolasi, shape key,
  rigid body, `clear_keyframes`
- **Scene/UV/Printing/Batch/Analysis/GN/IO**: tiga titik cahaya, kamera+track,
  render settings; unwrap manual background-safe; manifold/Euler, mm, bed layout;
  rename/duplikat batch; ringkasan scene/objek/datablock; GN scatter; export 10 format
- **Semua pesan runtime/log → Bahasa Indonesia** (modul, `_axsock`,
  `blender_connection`, `stdio_bridge`, deskripsi tool MCP)
- Audit API terhadap docs Blender (`data/api/`): `armature.symmetrize`
  (`NEGATIVE_X`/`POSITIVE_X`), vertex color per loop, `use_selection`/
  `selected_objects_only` pada export terpilih, path absolut render, penghapusan
  data blok per registry
- Blender 5.x: manifest `blender_version_min = 4.2.0`, gates versi di `compat.py`
- Verifikasi offline: `tests/bpy_stub.py` + `test_command_surface.py` menjalankan
  seluruh perintah terdokumentasi tanpa binary Blender (204 tes lulus; 105 tes Blender dilewati).

### Added — alur "dari nol" per dominio
- `model_from_scratch`, `rig_from_scratch`, `animate_from_scratch` melengkapi
  `colorize_from_scratch` yang sudah ada, sehingga keempat dominio punya satu
  panggilan yang merangkai alur penuh (buat → atur → modifier/tulang/keyframe).
  Sebelumnya agent harus merakit 3–5 panggilan manual yang bisa gagal separuh
  jalan dan meninggalkan scene setengah jadi.

### Fixed
- `assign_image_texture` hanya menyambungkan **Alpha** dan tidak pernah
  menyambungkan **Base Color**, sehingga tekstur yang dipasang tidak terlihat
  sama sekali saat render.
- `add_vertex_color` memakai `mesh.vertex_colors` (API lawas, terbatas pada
  Byte/CORNER). Sekarang memakai `color_attributes` dengan pilihan domain dan
  tipe data, serta tetap punya cadangan untuk Blender lama.
- Operasi tulang gagal di lingkungan tanpa view layer penuh. Kini turun kelas
  dengan rapi ke data API `edit_bones` selama API itu tersedia.
- `add_rigid_body` membuat rigid body world dua kali; blok duplikat dihapus.

### Changed
- 11 docstring publik yang tersisa di modul domain diterjemahkan ke Bahasa
  Indonesia (61/61 kini konsisten), karena teks ini ikut terbaca agent lewat
  `describe_tool`.



### Added — puente al catálogo de tools
- `addon/registry_bridge.py`: carga el `ToolRegistry` de `src/tools/**` dentro
  de Blender y lo expone por socket. Las **227 tools** ya existentes eran
  inalcanzables desde el cliente MCP, que sólo veía los 6 métodos `cmd_*`
  escritos a mano.
- Tools MCP `list_tools`, `describe_tool`, `call_tool` y `registry_status`
  para descubrir y ejecutar cualquier tool del catálogo.

### Added — lote transaccional
- `addon/transaction.py` y tool `run_batch`: ejecuta N operaciones bajo un
  único punto de restauración. Si una falla, la escena vuelve **exactamente**
  al estado previo en vez de quedar a medio construir.
- El rollback se **verifica**: `bpy.ops.ed.undo()` falla su `poll()` cuando no
  hay ventana (background, timers) y no revertía nada sin avisar. Ahora se
  comprueba el resultado y, si no surtió efecto, se restaura el censo y las
  transformaciones a mano.

### Added — consultas de escena
- `addon/inspect_scene.py` con `get_scene_graph`, `measure` y `find_objects`:
  jerarquía padre→hijo completa, dimensiones, materiales y modificadores;
  distancia entre centros y hueco real entre superficies (negativo si hay
  solape); búsqueda por nombre/tipo/complejidad/material.
  `get_scene_info` aplanaba la escena y truncaba a 20 objetos.

### Added — ensamblaje extendido
- `align_objects`, `distribute_objects` y `array_object`, construidos sobre el
  sistema de 27 anclas. Alinean por **bounding box real**, no por el origen
  del objeto, que suele estar descentrado.

### Fixed — seguridad
- El API HTTP (`:9877`) ejecutaba Python arbitrario en Blender sin
  autenticación y escuchando en `0.0.0.0` con `Access-Control-Allow-Origin: *`:
  RCE remoto. Ahora escucha en `127.0.0.1`, exige bearer token (comparado en
  tiempo constante) y restringe el origen CORS.
- `/api/execute` no validaba nada. Ahora pasa por la misma política y el mismo
  hilo que el socket, reutilizando su handler.
- El validador AST bloqueaba imports pero no la introspección: `getattr`
  deletreado y `().__class__.__bases__[0].__subclasses__()` recuperaban
  `builtins` y con ello `os`. Se bloquean atributos y nombres de introspección.
- El servidor HTTP tocaba `bpy` desde su propio hilo, lo que puede tumbar
  Blender. Todo acceso se marshala al hilo principal vía `bpy.app.timers`.

### Fixed — ensamblaje
- `get_bbox_anchors` aplicaba `matrix_world` **dos veces** (los córners ya
  venían transformados), así que las anclas caían lejos del objeto en cuanto
  éste no estaba en el origen. El bbox se calcula ahora en espacio local.
- `snap_and_parent` capturaba `matrix_world` antes de que el depsgraph
  reflejara el snap y luego lo restauraba, **anulando el movimiento** que
  acababa de hacer.
- El timeout de ejecución usaba `SIGALRM`, que no existe en Windows
  (`AttributeError` antes de ejecutar nada). Ahora es opcional y configurable
  con `BLENDER_MCP_EXEC_TIMEOUT`.

### Added
- High-level `create_model`, `animate_object`, and `color_object` MCP tools
- **128 MCP tools** exposed via FastMCP (`mcp_server.py`) and the SDK-less
  `stdio_bridge.py` from one spec (`mcp_tools.py`)
- Full **modeling** surface: primitives (CUBE/SPHERE/UVSPHERE/ICOSPHERE/
  CYLINDER/CONE/TORUS/MONKEY/GRID/CIRCLE/EMPTY) built with data API (works in
  `blender -b`), booleans, modifiers (18 types), bmesh bevel/extrude/inset,
  merge-by-distance, mesh cleanup, curves, 3D text, screw/lathe, join, apply
- Full **coloring** surface: PBR materials (Principled BSDF), shader node
  graph add/list/set/connect/remove, image textures, vertex colors, emission,
  transparency, one-shot colorize
- Full **rigging** surface: armatures, bones (edit mode), bone collections
  (4.0+), vertex groups + weights, object/pose constraints, IK chains,
  auto-rig weights, mirror, pose reset
- Full **animation** surface: keyframes, location/rotation/scale animation,
  multi-keyframe batches, actions, interpolation, timeline, shape keys,
  rigid body, gravity
- **Scene**: lights (point/sun/spot/area), three-point lighting, cameras +
  track-to, render engine/resolution/samples/device, scene summary, cleanup,
  purge, select/hide by type
- **UV**: background-safe unwrap (SMART/PLANAR/CUBE/SPHERE/CYLINDER), UV maps,
  texel density
- **3D printing**: manifold analysis (Euler + boundary loops), mm dimensions,
  wall thickness, print-bed layout, STL-mm export
- **Batch**: rename, delete-by-type, duplicate, scale/location, apply-all
- **Analysis**: scene/object summaries, blendfile datablock inventory, mesh
  topology health, polygon budget
- **Geometry Nodes**: GN modifier + node groups, instance scatter, node add
- **Import/export**: glb/gltf/fbx/obj/stl/ply/usd/usdz/dae/x3d, selected/scene
- Command registry `addon/handlers.py` — `_axsock` falls back to it after
  legacy `cmd_*` methods (114 commands total)
- **Blender 5.x support**: `blender_version_min = 4.2.0` (bone collections,
  EEVEE Next samples, `temp_override`, `new_from_object`), version gates in
  `addon/compat.py`; background-safe data-API code paths
- Offline test harness: `tests/bpy_stub.py` (fake bpy/bmesh/mathutils) drives
  the real dispatcher — 203 tests pass without a Blender binary
- `validate_tools.py` refactored: command list is importable data, runner
  guarded by `__main__`

### Fixed
- Installable wheel now includes the Python package, MCP server, socket client, and bundled API docs
- CLI now honors stdio/SSE transport selection and starts the packaged server
- Socket responses now propagate Blender errors and close connections deterministically
- Socket code execution now runs the AST safety validator before `exec`
- MCP SDK dependency pinned below the incompatible 2.x API
- Stale client-docs test used a hardcoded `/home/carlosh` path; now derived
  from the repo root; e2e socket tests skip when Blender is unreachable

## [1.0.0] - 2026-07-23

### Added
- **118 tools** across 16 categories
- **19 skills** for Claude Code/Cursor
- **Enterprise security**: AST validation, sandboxed execution, rate limiting
- **Performance**: LRU cache, tool result caching, lazy loading
- **MCP Adapter**: stdio to TCP bridge for opencode
- **Integration tests**: 16 tests with real Blender 5.2

### Security
- AST Validator with 200+ blocked patterns
- Sandboxed code execution with timeout protection
- Per-user rate limiting with token bucket algorithm
- Structured audit logging with file rotation
- Input validation for SQL injection, XSS, path traversal

### Performance
- LRU Cache with TTL support
- Tool result caching for repeated calls
- Lazy loading of tool categories
- Thread-safe cache operations

### Fixed
- `list()` builtin shadow in objects, materials, lights, modifiers
- Engine names: `BLENDER_EEVEE_NEXT` → `BLENDER_EEVEE` for Blender 5.2
- Mesh cleanup: `to_mesh_clear()` instead of `bpy.data.meshes.remove()`
- Color conversion: `[c for c in color]` instead of `list(color)`
- `active_object`/`selected_objects` for background mode with `getattr()`
- AST validator: custom blocked names now work correctly
- Input validator: added `import os` pattern

### Compatible with
- Blender 4.0+
- Blender 5.2 LTS
- Python 3.10+
- opencode, Claude Desktop, Cursor

## [0.8.125] - 2026-07-18

### Added
- MCP Server with 6 core tools
- Blender socket server on port 9876
- Basic security validation

### Fixed
- Port conflicts
- Import issues

## [0.8.0] - 2026-07-01

### Added
- Initial release
- Basic MCP server
- Blender addon
