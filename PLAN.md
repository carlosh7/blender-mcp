# blender-mcp — Plan de Desarrollo v0.8.52+

Prioridades: 🔴 Alta (semanal) | 🟡 Media (quincenal) | 🟢 Baja (mensual)

---

## Fase 1: Análisis de Escena (🔴 Prioridad Alta)

Implementar las tools de análisis que el oficial tiene y nosotros no.

| # | Tool | Archivo | Esfuerzo | Dependencia |
|---|------|---------|----------|-------------|
| 1.1 | `get_objects_summary` | `addon/handlers/analysis.py` | 2h | — |
| 1.2 | `get_object_detail_summary` | `addon/handlers/analysis.py` | 2h | 1.1 |
| 1.3 | `get_blendfile_summary_datablocks` | `addon/handlers/analysis.py` | 1h | 1.2 |
| 1.4 | Registrar en `src/blender_mcp/tools/` | `src/blender_mcp/tools/analysis.py` | 1h | 1.1-1.3 |
| 1.5 | Validar con `validate_tools.py` | — | 0.5h | 1.4 |

**Total:** ~6.5h

**Resultado:** El LLM podrá ver qué objetos hay, sus propiedades, y los data-blocks de la escena antes de generar código.

---

## Fase 2: Captura Visual como Imagen (🔴 Prioridad Alta)

| # | Tool | Archivo | Esfuerzo |
|---|------|---------|----------|
| 2.1 | `get_screenshot_of_window_as_image` (base64) | `addon/handlers/analysis.py` | 2h |
| 2.2 | Registrar tool MCP | `src/blender_mcp/tools/analysis.py` | 0.5h |
| 2.3 | Enviar imagen al LLM vía mensaje | `addon/auto_process.py` | 1h |

**Total:** ~3.5h

**Resultado:** El LLM podrá ver el resultado visual de su código.

---

## Fase 3: Correcciones y Calidad (🔴 Prioridad Alta)

| # | Tarea | Archivo | Esfuerzo |
|---|-------|---------|----------|
| 3.1 | Auto-seleccionar modelo de opencode al inicio | `addon/__init__.py` | 1h |
| 3.2 | No perder el modelo al reiniciar Blender | `addon/config_cache.py` | 0.5h |
| 3.3 | Forzar redibujo del chat cuando llega respuesta | `addon/auto_process.py` | 0.5h |
| 3.4 | Soporte Anthropic Claude vía REST | `addon/auto_process.py` | 2h |
| 3.5 | Soporte Ollama (local) vía REST | `addon/auto_process.py` | 2h |

**Total:** ~6h

---

## Fase 4: Documentación de API Embebida (🟡 Prioridad Media)

| # | Tool | Archivo | Esfuerzo |
|---|------|---------|----------|
| 4.1 | Generar/descargar docs RST de API Blender | `addon/docs/` | 3h |
| 4.2 | `search_api_docs(query)` | `addon/handlers/docs.py` | 3h |
| 4.3 | `get_python_api_docs(topic)` | `addon/handlers/docs.py` | 2h |
| 4.4 | Registrar tools MCP | `src/blender_mcp/tools/docs.py` | 0.5h |

**Total:** ~8.5h

**Resultado:** El LLM podrá buscar en la documentación oficial de Blender.

---

## Fase 5: Render y Viewport (🟡 Prioridad Media)

| # | Tool | Archivo | Esfuerzo |
|---|------|---------|----------|
| 5.1 | `render_viewport_to_path(filepath)` | `addon/handlers/render.py` | 1h |
| 5.2 | `jump_to_view3d_object_by_name(name)` | `addon/handlers/viewport.py` | 1h |

**Total:** ~2h

---

## Fase 6: Auto-diagnóstico y Test (🟡 Prioridad Media)

| # | Tarea | Archivo | Esfuerzo |
|---|-------|---------|----------|
| 6.1 | `blender-mcp --doctor` completo (5 checks) | `src/blender_mcp/doctor.py` | 1h |
| 6.2 | Test de integración con LLM real | `tests/test_e2e_llm.py` | 2h |
| 6.3 | CI/CD completo en GitHub Actions | `.github/workflows/test.yml` | 1h |

**Total:** ~4h

---

## Fase 7: Experiencia de Usuario (🟢 Prioridad Baja)

| # | Tarea | Archivo | Esfuerzo |
|---|-------|---------|----------|
| 7.1 | Botón "Copy Chat" siempre visible | `addon/panels/chat.py` | 0.5h |
| 7.2 | Indicador de conexión abierto/cerrado | `addon/panels/config.py` | 0.5h |
| 7.3 | Mensaje de ayuda cuando no hay LLM | `addon/auto_process.py` | 0.5h |
| 7.4 | Log de chat exportable a .txt | `addon/auto_process.py` | 0.5h |

---

## Resumen de Tiempos

| Fase | Prioridad | Horas |
|------|-----------|-------|
| 1: Análisis de Escena | 🔴 Alta | 6.5h |
| 2: Captura Visual | 🔴 Alta | 3.5h |
| 3: Correcciones | 🔴 Alta | 6h |
| 4: Documentación API | 🟡 Media | 8.5h |
| 5: Render | 🟡 Media | 2h |
| 6: Tests | 🟡 Media | 4h |
| 7: UX | 🟢 Baja | 2h |
| **Total** | | **~32.5h** |

---

## Archivos a Crear

| Archivo | Fase | Propósito |
|---------|------|-----------|
| `addon/handlers/analysis.py` | 1 | Tools de análisis de escena |
| `addon/handlers/docs.py` | 4 | Tools de documentación de API |
| `addon/handlers/viewport.py` | 5 | Tools de navegación en viewport |
| `src/blender_mcp/tools/analysis.py` | 1,2,4,5 | Registro de tools en FastMCP |
| `tests/test_e2e_llm.py` | 6 | Test de integración con LLM real |
| `.github/workflows/test.yml` | 6 | CI/CD |

---

## Versiones Planificadas

| Versión | Fase | Contenido |
|---------|------|-----------|
| v0.8.52 | 1 | `get_objects_summary`, `get_object_detail_summary` |
| v0.8.53 | 2 | `get_screenshot_of_window_as_image` |
| v0.8.54 | 3 | Auto-selección de modelo, Anthropic, Ollama |
| v0.8.55 | 4 | `search_api_docs`, `get_python_api_docs` |
| v0.8.56 | 5 | `render_viewport_to_path`, `jump_to_view3d` |
| v0.8.57 | 6 | Tests, CI/CD, doctor |
| v0.8.58 | 7 | UX improvements |

**Fin del plan.** Cada fase se puede ejecutar de forma independiente.
