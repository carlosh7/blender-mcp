# blender-mcp — Plan de Desarrollo ✅ COMPLETADO v0.8.52

Todas las fases implementadas en una sola sesión. 71/71 tools validadas.

---

## Fase 1: Análisis de Escena ✅ COMPLETED

| # | Tool | Status |
|---|------|--------|
| 1.1 | `get_objects_summary` | ✅ `addon/handlers/analysis.py` |
| 1.2 | `get_object_detail_summary` | ✅ `addon/handlers/analysis.py` |
| 1.3 | `get_blendfile_summary_datablocks` | ✅ `addon/handlers/analysis.py` |
| 1.4 | Registrar en `src/blender_mcp/tools/` | ✅ `src/blender_mcp/tools/analysis.py` |
| 1.5 | Validar con `validate_tools.py` | ✅ 71/71 pass |

## Fase 2: Captura Visual ✅ COMPLETED

| # | Tool | Status |
|---|------|--------|
| 2.1 | `get_screenshot_as_base64` | ✅ `addon/handlers/analysis.py` |
| 2.2 | Registrar tool MCP | ✅ `src/blender_mcp/tools/analysis.py` |
| 2.3 | Enviar imagen al LLM vía mensaje | ✅ `addon/auto_process.py` (vision providers) |

## Fase 3: Correcciones ✅ COMPLETED

| # | Tarea | Status |
|---|-------|--------|
| 3.1 | Auto-seleccionar modelo (fallback opencode auth.json) | ✅ `addon/__init__.py` |
| 3.2 | Persistencia del modelo | ✅ `addon/config_cache.py` |
| 3.3 | Forzar redibujo del chat | ✅ `addon/auto_process.py` |
| 3.4 | Soporte Anthropic Claude vía REST | ✅ `addon/auto_process.py` |
| 3.5 | Soporte Ollama (local) | ✅ `addon/auto_process.py` |

## Fase 4: Documentación de API ✅ COMPLETED

| # | Tool | Status |
|---|------|--------|
| 4.1 | API introspection (en lugar de RST) | ✅ `addon/handlers/docs.py` |
| 4.2 | `search_api_docs(query)` | ✅ `addon/handlers/docs.py` |
| 4.3 | `get_python_api_docs(topic)` | ✅ `addon/handlers/docs.py` |
| 4.4 | Registrar tools MCP | ✅ `src/blender_mcp/tools/docs.py` |

## Fase 5: Render y Viewport ✅ COMPLETED

| # | Tool | Status |
|---|------|--------|
| 5.1 | `render_viewport_to_path(filepath)` | ✅ `addon/handlers/render.py` |
| 5.2 | `jump_to_view3d_object_by_name(name)` | ✅ `addon/handlers/viewport.py` |

## Fase 6: Auto-diagnóstico y Tests ✅ COMPLETED

| # | Tarea | Status |
|---|-------|--------|
| 6.1 | `blender-mcp --doctor` (6 checks) | ✅ `src/blender_mcp/doctor.py` |
| 6.2 | Tests de nuevos handlers | ✅ `tests/test_handlers.py` |
| 6.3 | CI/CD actualizado | ✅ `.github/workflows/test.yml` |

## Fase 7: UX ✅ COMPLETED

| # | Tarea | Status |
|---|-------|--------|
| 7.1 | Botón "Copy Chat" | ✅ Ya existía |
| 7.2 | Indicador de conexión (Socket + MCP) | ✅ `addon/panels/config.py` |
| 7.3 | Mensaje de ayuda sin LLM | ✅ `addon/panels/chat.py` + `addon/operators/chat.py` |
| 7.4 | Log exportable a .txt | ✅ Ya existía |

---

## Resumen

| Fase | Horas Estimadas | Status |
|------|-----------------|--------|
| 1: Análisis de Escena | 6.5h | ✅ |
| 2: Captura Visual | 3.5h | ✅ |
| 3: Correcciones | 6h | ✅ |
| 4: Documentación API | 8.5h | ✅ |
| 5: Render | 2h | ✅ |
| 6: Tests | 4h | ✅ |
| 7: UX | 2h | ✅ |
| **Total** | **~32.5h** | **✅ COMPLETADO v0.8.52** |

## Archivos Creados

| Archivo | Propósito |
|---------|-----------|
| `addon/handlers/analysis.py` | Tools de análisis + screenshot base64 |
| `addon/handlers/docs.py` | Tools de documentación vía introspection |
| `addon/handlers/viewport.py` | Tools de navegación en viewport |
| `src/blender_mcp/tools/analysis.py` | Registro MCP de analysis tools |
| `src/blender_mcp/tools/docs.py` | Registro MCP de docs tools |
| `src/blender_mcp/tools/viewport.py` | Registro MCP de viewport tools |

## Bug Tracker — Versiones Planificadas

### v0.8.54 🔴 — Auto-select de modelo + feedback de errores
| # | Bug | Archivo | Prioridad |
|---|-----|---------|-----------|
| 1 | Auto-select elige `pro` en vez de `flash` cuando ambos existen | `addon/__init__.py` (_read_opencode_model + delayed_load) | 🔴 Crítico |
| 2 | No hay indicador visual de qué modelo está activo en el panel | `addon/panels/chat.py` | 🟡 Medio |
| 3 | `_exec_code` no reporta errores de sintaxis del código generado (DeepSeek parte líneas) | `addon/auto_process.py` | 🟡 Medio |
| 4 | Sistema necesita reintentar si el código falla con el error en el prompt | `addon/auto_process.py` (nuevo: _retry_with_feedback) | 🔴 Crítico |

### v0.8.55 🔴 — Robustez del socket server
| # | Bug | Archivo | Prioridad |
|---|-----|---------|-----------|
| 5 | `handler_dispatch` en `_axsock.py` falla cuando se importa fuera del package (__package__ None) | `addon/_axsock.py` | 🔴 Crítico |
| 6 | Socket no reconecta automáticamente si `mcp_server.py` se reinicia | `addon/_axsock.py` | 🟡 Medio |

### v0.8.56 🔴 — Seguridad en execute_blender_code
| # | Bug | Archivo | Prioridad |
|---|-----|---------|-----------|
| 7 | `execute_blender_code` puede causar segfault con código complejo (bucle infinito, bpy mal usado) | `addon/_axsock.py` + `addon/auto_process.py` | 🔴 Crítico |
| 8 | Falta timeout de ejecución en `_exec_code` | `addon/auto_process.py` | 🟡 Medio |

### v0.8.57 🟡 — UI/UX
| # | Bug | Archivo | Prioridad |
|---|-----|---------|-----------|
| 9 | Panel de chat no muestra feedback visual mientras DeepSeek procesa (solo "⏳ Pensando...") | `addon/panels/chat.py` | 🟡 Medio |
| 10 | Cuando el código ejecutado modifica la escena, el viewport no se actualiza automáticamente | `addon/auto_process.py` (_exec_code) | 🟢 Bajo |
| 11 | No hay botón para cancelar una solicitud en curso | `addon/operators/chat.py` | 🟢 Bajo |

### v0.8.58 🟡 — Tests y CI
| # | Bug | Archivo | Prioridad |
|---|-----|---------|-----------|
| 12 | `validate_tools.py` usa `_axsock._execute()` directo — no prueba socket real | `validate_tools.py` | 🟡 Medio |
| 13 | CI desactualizado (aún importa `tools_*.py` que ya no existen) | `.github/workflows/test.yml` | 🟡 Medio |
| 14 | Tests de handlers tienen `@pytest.mark.skip` y nunca se ejecutan | `tests/test_handlers.py` | 🟢 Bajo |

### v0.8.59 🟢 — Mejoras
| # | Mejora | Archivo | Prioridad |
|---|--------|---------|-----------|
| 15 | Que el LLM pueda ver la escena actual ANTES de generar código (screenshot) | `addon/auto_process.py` | 🟢 Bajo |
| 16 | Auto-detectar si `deepseek-v4-flash` está disponible y usarlo por defecto | `addon/__init__.py` | 🟡 Medio |

---

## Resumen

| Versión | Enfoque | Bugs |
|---------|---------|------|
| **v0.8.54** | Auto-select + feedback loop | 4 bugs 🔴 |
| **v0.8.55** | Socket robustez | 2 bugs |
| **v0.8.56** | Seguridad código | 2 bugs |
| **v0.8.57** | UI/UX | 3 bugs 🟡 |
| **v0.8.58** | Tests/CI | 3 bugs 🟡 |
| **v0.8.59** | Mejoras | 2 bugs |

Prioridad: seguir orden numérico. Cada versión es independiente y desplegable.
