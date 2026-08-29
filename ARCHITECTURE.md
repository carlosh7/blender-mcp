# Arquitectura de blender-mcp-ultra

## Flujo principal (cliente MCP externo)

```
Agente IA (Claude/Cursor/opencode/ZCode…)
       │  MCP stdio (o --sse en :9879)
       ▼
mcp_server.py — gateway FastMCP canónico
       │  · registra 245 tools (6 base + 239 del registry) leyendo los
       │    metadatos en LOCAL (no requiere Blender arriba)
       │  · modo lite (--lite / BLENDER_MCP_LITE=1): 24 tools núcleo +
       │    tools_search + tool_execute (~4k tokens de contexto vs ~30k)
       │  · code_guard valida execute_blender_code en el gateway
       ▼  socket TCP 127.0.0.1:9876 · token obligatorio
addon/_axsock.py (dentro de Blender)
       │  · auth por token (auto-generado en <config>/blender-mcp/socket_token)
       │  · serializa todo bpy al hilo principal vía bpy.app.timers
       │  · ~60 comandos cmd_* (ping, renders, snapshots, scene_lock…)
       ▼
mcp_ultra/ (ToolRegistry cargado in-process)
       │  · 239 tools en 16 categorías; handlers ejecutan bpy
       ▼
Blender (escena, render, physics, geonodes…)
```

Puntos clave del diseño:

- **El orden de arranque no importa**: el gateway construye el mismo
  `ToolRegistry` que el addon (fuente de verdad única en `mcp_ultra/tools/`)
  en su propio proceso. Si una tool se llama con Blender cerrado, devuelve
  un error claro y funciona en cuanto Blender se abra (reconexión por llamada).
- **Una sola conexión de socket compartida**, serializada con lock por
  petición (`blender_connection.py`) para que llamadas MCP concurrentes no
  crucen respuestas.
- **Multi-agente**: lock de escena advisory (`scene_lock`) y bus de eventos
  (`poll_events`) en el addon.

## Componentes

| Componente | Rol |
|------------|-----|
| `mcp_server.py` | Gateway MCP canónico (FastMCP). Registro local del registry, modo lite, `--sse` |
| `blender_connection.py` | Cliente socket con lock + resolución del token compartido |
| `mcp_ultra/tools/` | Fuente de verdad de las 239 tools (TOOLS + HANDLERS por módulo) |
| `mcp_ultra/presentation/mcp_server/` | Server FastMCP alternativo in-process (modo bpy, entry `blender-mcp-server`) |
| `mcp_ultra/infrastructure/security/` | InputValidator (inyección/path traversal en parámetros); el AST guard real es `addon/code_guard.py` |
| `addon/_axsock.py` | Servidor socket :9876 dentro de Blender; auth, timers, cmd_* |
| `addon/code_guard.py` | Blocklist AST (~80 patrones) para `execute_code` |
| `addon/rst_search.py` | Búsqueda TF-IDF sobre los RST de la API de Blender (`data/api`) |
| `addon/server/mini_http.py` | REST opcional :9877 (token + guard) |
| `addon/assembly.py` / `spatial.py` / `scanner.py` | Snap de 27 anclas, validador de colisiones BVH, blueprints |
| `blender_mcp/` | CLI (`blender-mcp`), doctor, paths cross-OS, launcher headless |
| `scripts/` | CI headless, sesión persistente host, índice de tools, fetch de docs |

## Seguridad

| Capa | Mecanismo |
|------|-----------|
| Transporte | Solo localhost; token obligatorio en :9876 (auto-generado, 0600, compartido addon↔gateway vía `<config>/blender-mcp/socket_token`) |
| Ejecución de código | `code_guard` (AST blocklist) en gateway **y** addon + timeout SIGALRM 10s + undo automático |
| Multi-agente | Lock de escena advisory para comandos mutadores |
| Auditoría | Logs JSON estructurados con rotación; gitleaks + bandit + pip-audit en CI |

## Testing

```
tests/unit/         sin Blender (bpy con stub)
tests/integration/  requieren socket :9876 activo (skip automático)
tests/e2e/          workflows completos vía gateway MCP (MCPSession)
CI                  Blender headless real en Linux/Windows/macOS
```

## Historia (resumen)

- v1/v2: gateway de 6 tools + chat interno del addon (eliminado en la
  limpieza post-3.1: `auto_process`, gateways `mcp_adapter`/`start_server`,
  pila "AXIOM" — ver CHANGELOG Unreleased).
- v3.x: registry de 239 tools, arquitectura hexagonal en `mcp_ultra/`
  (antes `src/`), VLM feedback, inteligencia espacial, modo lite.
