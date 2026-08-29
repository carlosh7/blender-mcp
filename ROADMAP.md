# blender-mcp-ultra — Roadmap vivo

> Última actualización: v3.2.0. Sustituye al plan histórico de fases 0-9 (2025),
> que sigue disponible en el historial de git.
> Estado real del código y decisiones de diseño; pendientes al final.

## Estado actual (v3.2.0)

| Área | Estado |
|---|---|
| Gateway MCP | `mcp_server.py` canónico: 248 tools (7 base + 241 registry), registro local (sin requerir Blender), modo lite (26 tools, ~4k tokens) |
| Protocolo | Socket :9876 con framing v2 (`BMCP`+len+JSON) negociado; legacy compatible con addons viejos |
| Seguridad | Token obligatorio compartido (archivo 0600), code_guard AST en gateway **y** addon, rate limit + body cap en REST, sin SO_REUSEPORT |
| Addon | Transporte/auth/eventos extraídos (`socket_protocol/socket_auth/socket_events`); ejecución bpy serializada al hilo principal |
| Contenido | 22 guías de workflow servidas como tools (`guidance.*`) y como resource (`blender://guidance/{topic}`) |
| Empaquetado | Wheel: `blender_mcp` + `mcp_ultra` (sin paquetes top-level `src`/`addon`/`config`); extensión con registry bundled |
| Tests | ~430 tests (unit/integration/e2e), escena aislada para e2e, CI Linux+Blender headless con coverage, Windows/macOS con e2e |
| MCP avanzado | Prompts (product_shot/archviz/simple_scene), resources (escena + guías), annotations por tool |

## Decisiones de diseño (cerradas)

- **Integraciones de assets**: viven en el addon (`cmd_search_assets` →
  PolyHaven/Sketchfab/Hyper3D/AmbientCG). La capa `mcp_ultra/adapters/`
  (LLM/assets/storage) era código sin cablear y fue **eliminada**; si en el
  futuro se quieren integraciones server-side, se construyen como tools del
  registry, no como capa de adapters paralela.
- **Skills instalables**: eliminadas como mecanismo. El contenido viaja en
  el MCP (`guidance.list/get`, resource `blender://guidance/{topic}`) —
  cero fricción para el usuario.
- **Modo full vs lite**: en 3.x el default es **full** (compatibilidad);
  pasar lite a default se decide en **4.0** (rompe expectativas de clientes
  que esperan ver el catálogo completo; requiere anuncio previo).

## Pendientes (priorizados)

| # | Ítem | Horizonte | Notas |
|---|------|-----------|-------|
| 1 | Publicar 3.2.0 en PyPI (`twine upload dist/*` — requiere credenciales del mantenedor) | corto | artefactos listos en `dist/` |
| 2 | `docker/` oficial con render GPU (nvidia-container-toolkit) + docs de headless en nube | medio | Dockerfile actual es CPU |
| 3 | Extraer renders/chat de `_axsock.py` (fase 2 del split: `socket_renders.py`, `socket_chat.py`) | medio | fase 1 hecha: auth/eventos/protocolo |
| 4 | Pool de sockets para llamadas concurrentes reales (hoy 1 lock por gateway) | medio | ver docs/concurrency.md |
| 5 | Observabilidad: métricas por tool (latencia/errores) en `/api/health` y logs JSON | medio | `infrastructure/monitoring` existe sin cablear |
| 6 | Tests de integración para prompts/resources en clientes reales (Claude Desktop, Cursor) | medio | |
| 7 | Soporte Blender LTS 4.2/4.5 explícito en la matriz de CI | medio | hoy solo 5.1 |
| 8 | Telemetría opt-in (off por defecto) con panel de preferencias | largo | módulos ya existen sin usar |
| 9 | i18n de guías (ES/EN) servida según locale del cliente | largo | |

## Visión

Ser el estándar para que cualquier agente IA modele, texturice, simule y
renderice en Blender: registro de tools viva, seguridad verificable,
contenido de técnica incluido y cero fricción de instalación.
