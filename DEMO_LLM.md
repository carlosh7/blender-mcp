# Demo End-to-End: LLM Nyata → MCP → Blender Headless

Demo ini membuktikan seluruh rantai runtime berfungsi di Blender 4.2.23 LTS
headless (`blender -b`), dikendalikan oleh model LLM nyata (`gpt/gpt-5.6-sol`
via OpenAI-compatible API) yang memilih dan memanggil tool MCP satu per satu.

## Alur

```
Prompt adegan (meja, vas, bola, lantai, kursi)
  -> LLM gpt-5.6-sol (vibe.madewgn.dev/v1)
  -> deretan aksi JSON [{"tool": ..., "args": {...}}]
  -> BlenderConnection.send_command()  (blender_connection.py)
  -> socket TCP :9876
  -> addon/_axsock.py  (headless: antrean + pump main-thread)
  -> addon/handlers.py -> modeling/materials/animation/rigging/scene_tools
  -> render_frame() -> PNG
```

## Hasil

| Render | Isi |
|--------|-----|
| `demo_artifacts/render_1.png` | Frame 1: meja kayu, vas kaca biru, bola logam, kursi hijau, lantai; kamera (6,-6,4) |
| `demo_artifacts/render_2.png` | Frame 60: bola logam teranimasi (lokasi + rotasi) |
| `demo_artifacts/render_3.png` | Sudut kamera kedua (-7,-4,5), render ulang |

## Aksi yang dieksekusi (34 pada putaran 1)

- **Modeling**: `create_object` (CUBE/CYLINDER/SPHERE/GRID), `transform_object` (lokasi + skala)
- **Coloring**: `create_material` ×5 (kayu, kaca transmission+ior, logam metallic, lantai, hijau), `assign_material` ×5
- **Animation**: `animate_location` + `animate_rotation` (bola, frame 1..120)
- **Rigging**: `create_armature` (root bone), `rig_from_scratch` (kursi, MODIFIER_ONLY), `add_armature_modifier`
- **Scene/Render**: `create_camera`, `create_light` (AREA 300 W), `set_render_engine` (CYCLES), `set_render_resolution` (800×600), `render_frame` ×2

## Perbaikan yang dihasilkan dari demo

1. **Eksekusi socket headless**: server socket memakai `bpy.app.timers` yang
   tidak pernah berjalan di `blender -b`. Kini perintah headless masuk antrean
   dan dipompa di main-thread via `BlenderSocketServer.process_pending()`
   (skrip host), sehingga bpy tetap aman dan operator UI (mode_set) berfungsi.
2. **`_wrap` propagasi error**: hasil handler `{"error": ...}` kini dilaporkan
   sebagai `status: error`, bukan sukses palsu.
3. **`set_render_range` toleran urutan**: start > end ditukar otomatis;
   start == end ditolak dengan pesan jelas.
4. **Bug Blender nyata yang diperbaiki**: `BMLayerCollection.new()` posisional,
   `abs()` pada mathutils.Vector, akses bmesh setelah `bm.free()`,
   `NodeTree.interface.new_socket` (4.2+), fallback `bpy.types` pada
   `get_python_api_docs`.

## Verifikasi

- 204 tes offline lulus, 105 tes Blender dilewati tanpa binary.
- 70/70 + 1 UI-skip perintah inti di Blender 4.2.23 nyata.
- 66/66 + 1 UI-skip permukaan diperluas (bmesh, GN, rig, animasi, UV, render, ekspor) di Blender nyata.
- Socket end-to-end headless: ping, scene info, create, material, animasi, workflow — semua lewat TCP :9876.

## Cara menjalankan ulang

```bash
# 1. Host socket Blender headless (main-thread pump)
blender -b --python /tmp/socket_host.py &

# 2. Orkestrator demo (butuh API key OpenAI-compatible)
python /tmp/demo_orchestrator.py
```
