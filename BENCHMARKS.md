# BENCHMARKS.md — blender-mcp-ultra

Generado: 2026-08-24 (fase 4) · Python 3.14.4 · Blender 5.1.2 (GUI, :9876)

## Registro y dispatch (en proceso, sin Blender)

| Métrica | Valor |
|---|---|
| Registro de **147 tools** | mediana 0.0 ms |
| Dispatch `scene.get_info` (in-process) | mediana 0.0 ms · p95 0.01 ms |

## Transporte socket (:9876, Blender vivo)

| Métrica | Valor |
|---|---|
| `ping` round-trip (n=50) | mediana 5.2 ms · p95 5.3 ms |
| `execute_code` trivial (n=10) | mediana 7.3 ms |
| Overhead de dispatch vía socket (tool simple) | ~1-3 ms sobre el ping |

## Notas

- El coste dominante por operación es el round-trip de red local (~5 ms), no el registry.
- `rst_search_ms` (docs de bpy.ops): mediana 69 ms.
- Los renders pesados deben ir por `render.render_bg` (subprocess headless) para no bloquear la GUI.
