# ACTION_PLAN.md — blender-mcp (fork carlosh7)

Prioridad P0 = esta semana · P1 = este mes · P2 = backlog. No incluye commits automáticos.

## P0 — Seguridad (bloqueante)

- [x] 1. **Cerrar RCE de `addon/server/mini_http.py`**
   - Línea 141: `("0.0.0.0", 9877)` → `"127.0.0.1"`.
   - Exigir token (header `X-API-Token`, generado en preferencias del addon y guardado como `PASSWORD` en `Scene`); rechazar sin token.
   - Enrutar `POST /api/execute` por `AxiomValidator`/`input_validator` antes de `exec`.
   - Quitar `Access-Control-Allow-Origin: *` (o restringir a orígenes conocidos) — líneas 32 y 42.
   - Añadir test: request sin token → 401; con token + código prohibido → bloqueado.
- [x] 2. **Auth/token también en `_axsock.py` (9876)**: handshake con nonce o token en primer mensaje; documentar que debe quedar en localhost.
- [x] 3. **Sandbox en el path principal**: `execute_blender_code` (`mcp_server.py:39`) debe usar `WeakSandboxForLLM` + `input_validator.validate()` por defecto (flag opt-out solo en dev).
4. [x] **Secretos**: verificar que la clave demo Hyper3D (`k9TcfFoEhNd9…`) nunca vuelva al árbol; considerar `gitleaks protect` en CI y purga de historia si procede.
   - Árbol actual: 0 leaks (gitleaks detect --no-git, 2026-08-24).
   - CI: job `secrets` con `gitleaks/gitleaks-action@v2` (historia completa).
   - ⚠ Historia: quedan 4 hallazgos en commits de mayo 2026 (`addon/properties.py`, `addon/handlers/hyper3d.py` — clave demo heredada del upstream). Purga definitiva con git-filter-repo pendiente de decisión del mantenedor (reescribe historia compartida).

## P0 — Bugs que rompen el producto

- [x] 5. **Arreglar exposición MCP de los "118+ tools"** (`src/presentation/mcp_server/__init__.py:110-118`): eliminar el handler dummy; usar closure real:
   ```python
   def _register(mcp, registry, tool):
       @mcp.tool(name=tool.name.replace(".", "_"), description=tool.description)
       def handler(**kwargs):
           return json.dumps(registry.execute_tool(tool.name, kwargs).to_dict())
   ```
   Test e2e: listar tools del servidor FastMCP y assert count > 100.
- [x] 6. **Eliminar imports absolutos `core`/`tools`** → imports relativos (`from ..core.entities import …`) o empaquetar `src` como `blender_mcp_ultra/`. Quitar `sys.path.insert` de línea 12. Verificar con `uv pip install -e . && python -c "import blender_mcp_ultra"` en venv limpio.
- [x] 7. **Pin de dependencias**: `mcp[cli]>=1.3.0,<2` (o migrar a paquete `fastmcp`); añadir pins mínimos a `requirements.txt`. Motivo: `mcp==2.0.0` elimina `mcp.server.fastmcp` y hoy **ningún servidor arranca**.
- [x] 8. **Rutas absolutas `/home/carlosh`**: sustituir por `pathlib.Path(__file__).resolve().parents[N]` en `tests/integration/test_multi_client.py:23,43,63,85,119`, `test_suite.py:7`, `create_pixar_lamp_pro.py:2`, `create_pixar_lamp_perfect.py:2`. Meta: suite 100% verde en cualquier máquina.

## P1 — Calidad y CI

- [x] 9. **Formateo**: ejecutar el "formateo pendiente" del último commit: `ruff check . --fix --select I001,W293,W291,F401,F541,E701,E401` + `ruff format .`; luego revisar manualmente los 103 `bare-except` → `except Exception` (o logging).
- [x] 10. **F821 (56)**: triage uno a uno; cada nombre indefinido es un bug latente.
- [x] 11. **CI (GitHub Actions)**: matrix 3.10/3.12/3.14 con `ruff check`, `bandit -q -ll -r src addon`, `pytest`, `pip-audit`, `gitleaks protect --staged`. Fallar el build en HIGH bandit y en cualquier leak nuevo.
- [x] 12. **MD5 HIGH (bandit)**: `addon/asset_cache.py:51` y `addon/version_control.py:183` → `hashlib.md5(…, usedforsecurity=False)` o SHA-256.
- [x] 13. Consolidar a **un solo servidor MCP** (decidir: el de `src/` una vez arreglado, o el minimalista de raíz) y deprecar los demás con avisos claros en README/CHANGELOG.

## P2 — Producto y diseño

- [x] 14. **Alinear claims con realidad**: bajar "Production/Stable" a beta hasta P0 completado; auditar los "100% PRO" (varios módulos `addon/` tienen tests mínimos); marcar qué módulos están cableados al registry vs huérfanos (hay ~65 módulos en `addon/` y 235 defs de tools — generar matriz módulo↔tool↔test).
- [x] 15. **Runtime headless**: añadir `make test-headless` (pytest sin Blender) y modo smoke `python -m blender_mcp_ultra --check-path` que valide imports sin GUI; documentar limitaciones (sin screenshot/render sin Blender).
- [x] 16. **Docs**: fusionar README.md / README_ULTRA.md / GUIDE.md; mantener un único diagrama de arquitectura (hoy conviven "Axiom v2/v3", "FASE 1-6" y README público con números distintos).

## Criterio de cierre P0

- [x] gitleaks/bandit sin HIGH nuevos; mini_http solo localhost + token (verificado con exploit).
- [x] Servidor MCP arranca con deps frescas: raíz 6 tools E2E + src 118 tools stdio E2E.
- [x] `pytest` verde: **420 passed / 0 failed / 8 skipped** (2026-08-24, sesión de reanudación; e2e requieren Blender vivo).
- [x] `pip-audit` limpio ("No known vulnerabilities found", 2026-08-24). CI nuevo en `.github/workflows/ci.yml` (lint+secrets+test matrix 3.10/3.12/3.14+security); "en verde" pendiente del primer push.

## P0 — Nuevos hallazgos runtime (auditoría con Blender 5.1.2, 2026-08-24)

Ver evidencia completa en `AUDIT_REPORT.md` § Anexo runtime.

- [x] 15. **Arreglar doble registro del addon** (`addon/__init__.py:253+262`): o bien quitar `ui_classes`/`ai_classes` de la tupla `classes`, o bien no llamar `ui_register()`/`ai_register()`. Hoy el addon **no se puede activar** (`ValueError: already registered 'MCP_UL_TextTo3D'`). Test: `blender --background --python-expr "import addon; addon.register()"` sin traceback.
- [x] 16. **Corregir mapeo de `bound_box`** (`addon/anchor_system.py:60-67`): usar el orden real de Blender (`0:(-,-,-) 1:(-,-,+) 2:(-,+,+) 3:(-,+,-) 4:(+,-,-) 5:(+,-,+) 6:(+,+,+) 7:(+,+,-)`) o derivar anclas de `min/max` por eje en lugar de índices fijos. Test: `snap_and_parent(BOTTOM_CENTER→TOP_CENTER)` debe dejar el objeto en Z, no en X.
- [x] 17. **`_introspect_ops` sin `max_results`** (`addon/rst_search.py:150` vs `:183`): añadir el parámetro y propagarlo. Hoy `search_api_docs` crashea siempre que cae al fallback.
- [x] 18. **Añadir `pyyaml` a dependencies** (pyproject) o arreglar `_parse_yaml_basic` para YAML anidado; `get_settings()` crashea en installs limpios (`settings.py:160`).
- [x] 19. **Imports de `helpers` en tests**: añadir `tests` a `pythonpath` en pyproject o convertir a `from tests.helpers import …`. Hoy la suite no se recolecta sin `PYTHONPATH=tests`.
- [x] 20. **Eliminar handlers duplicados** en `addon/_axsock.py` (`cmd_snap_and_parent`, `cmd_snap_to_anchor`: líneas 248/257 vs 769/782) y alinear la doc de anclas de `mcp_server.py:70-71` con `ANCHOR_NAMES` real (`FRONT_BOTTOM_LEFT`, `CENTROID`, …).
