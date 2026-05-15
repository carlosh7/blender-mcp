# Arquitectura de blender-mcp

## Flujo

El sistema tiene dos caminos de entrada que convergen en el mismo backend:

### Camino A: Chat interno de Blender

```
Usuario escribe en chat Blender
       ↓
addon/auto_process.py  →  LLM API (function calling)
       ↓                        ↓
  search_api_docs()        execute_blender_code()
  (búsqueda en RST         (ejecuta código bpy)
   o introspección)
       ↓
  auto_process.py recibe resultado, exec el código
       ↓
  [undo_push] → [exec] → [validate_geometry]
```

### Camino B: Cliente MCP externo (opencode, Claude, Cursor)

```
Cliente MCP → mcp_server.py (6 tools) → socket TCP :9876
       ↓
addon/_axsock.py (cmd_*) → ejecuta en main thread de Blender
```

## Componentes

| Archivo | Rol |
|---------|-----|
| `addon/auto_process.py` | Orquesta LLM: envía mensaje, maneja function calling, ejecuta código |
| `addon/rst_search.py` | Buscador TF-IDF sobre 2,062 RSTs de la API de Blender |
| `addon/_axsock.py` | Servidor socket TCP :9876 dentro de Blender |
| `addon/assembly.py` | AssemblyEngine: snap de 27 anclas, parenting, simetría |
| `addon/spatial.py` | GeometryValidator: detección BVH de colisiones |
| `addon/scanner.py` | GeometryScanner: blueprint de 27 anclas |
| `mcp_server.py` | Servidor MCP externo, 6 tools |
| `blender_connection.py` | Cliente socket para conectar a Blender |

## Antes vs Después

```
Antes:   94 tools MCP + 22 handlers + agent_host + http_bridge + 300 líneas prompt
Después: 6 tools + docs search + 25 líneas prompt
```

## Seguridad

- Código envuelto en `undo_push` → reversible
- Timeout de 2s en búsquedas de documentación
- Las funciones prohibidas (`os`, `sys`, `subprocess`) se filtran vía AST
