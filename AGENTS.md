# blender-mcp — Agent Knowledge (Axiom v3.0 Edition)

Este archivo define las leyes globales para cualquier agente IA operando blender-mcp.

## ⚖️ Reglas de Oro (Inquebrantables)

1. **Buscar antes de ejecutar**: Antes de escribir CUALQUIER código bpy, llama a `search_api_docs(consulta)` para encontrar la API correcta. No inventes nombres de funciones.
2. **Cero Coordenadas Manuales**: No uses `obj.location = (x, y, z)`. Usa siempre `snap_and_parent` o `snap_to_anchor`.
3. **Validar después de ensamblar**: Tras cada snap, ejecuta `validate_geometry()` para detectar colisiones.
4. **Estándar de Nomenclatura de Anclas**: Formato `A_X_Y_Z` donde X,Y,Z pueden ser `MIN`, `CENTER` o `MAX`.
5. **No hardcodear URLs**: Usa `os.environ.get()` con fallback a `localhost` para servicios locales (Ollama, opencode, Blender socket).

## 🏗️ Workflow

1. **Consultar**: `search_api_docs(query)` para aprender la API correcta.
2. **Inspeccionar**: `get_scene_info()` para conocer el estado actual.
3. **Ejecutar**: `execute_blender_code(code)` con el código correcto (basado en docs).
4. **Ensamblar**: `snap_and_parent()` con sistema de 27 anclas.
5. **Validar**: `validate_geometry()` para verificar colisiones.

## 🧪 Testing

### Estructura de tests
```
tests/
├── helpers.py              # is_blender_available(), skip_without_blender
├── conftest.py             # Configuración pytest, MockBpy
├── test_handlers.py        # 18 categorías de tools (src.tools.*)
├── test_e2e_socket.py      # Tests socket con guarda skip_without_blender
├── unit/
│   └── test_tools.py       # Tests unitarios de tools
├── e2e/
│   ├── test_real_tools.py  # Tests reales con Blender
│   └── test_e2e_workflows.py
├── integration/
│   ├── test_blender_integration.py
│   ├── test_multi_client.py
│   └── test_stress.py
└── validate_*.py           # Scripts de validación manual
```

### Ejecutar tests
```bash
# Suite completa
pytest

# Solo tests de handlers (sin Blender)
pytest tests/test_handlers.py tests/unit/test_tools.py -v

# Tests que requieren Blender activo en :9876
pytest tests/test_e2e_socket.py -v
```

### Convenciones
- Los tests que requieren Blender usan `@skip_without_blender` de `helpers.py`
- Los tests que requieren `bpy` usan `pytest.importorskip("bpy")`
- `conftest.py` inyecta `MockBpy` en `sys.modules` cuando bpy no está disponible

## 📁 Estructura del Proyecto

```
blender-mcp/
├── addon/                      # Addon de Blender
│   ├── __init__.py             # Registro del addon
│   ├── _axsock.py              # Socket server TCP :9876
│   ├── core/                   # Motores fundamentales
│   │   ├── mesh_engine.py      # 17 primitivas + booleanos + subdivision
│   │   ├── texture_engine.py   # 50+ PBR materials + procedural
│   │   ├── rig_engine.py       # Armature + IK/FK + auto-rig
│   │   └── animation_engine.py # Keyframes + walk/run + facial
│   ├── organic/                # Sistema orgánico
│   │   └── character_gen.py    # 5 tipos de personajes
│   ├── physics/                # Simulación física
│   │   └── physics_engine.py   # Rigid/Soft/Fluid/Particles
│   ├── ai/                     # Asistente IA
│   │   └── ai_assistant.py     # Text→3D + Image→3D + Voice
│   ├── perception/             # Sistema de visión
│   │   └── perception_system.py # Scanner + Analyzer + Decision
│   ├── libraries/              # Bibliotecas
│   │   └── libraries.py        # 50+ materials + 20+ animations
│   ├── export/                 # Exportación
│   │   └── export_engine.py    # Unity/Unreal/glTF/STL/LOD
│   ├── creation_rules.py       # Dimensiones, conexiones, colecciones
│   ├── state_manager.py        # Persistencia, backup, historial
│   ├── validator.py            # Validación visual, dimensiones
│   └── ...                     # Otros módulos existentes
├── src/                        # Clean Architecture
│   ├── core/                   # Entidades e interfaces
│   ├── tools/                  # 19 categorías de tools
│   ├── adapters/               # Adaptadores
│   └── infrastructure/         # Cache, logging, security
└── tests/                      # Suite de tests
```

## 🔌 Puertos

| Puerto | Servicio | Configuración |
|--------|----------|---------------|
| 9876 | Blender Socket TCP | `BLENDER_PORT` env var |
| 9877 | HTTP REST API | hardcoded en addon |
| 9879 | MCP SSE Server | hardcoded en addon |
| 45677 | opencode SSE | `OPENCODE_SSE_URL` env var |
| 11434 | Ollama API | `OLLAMA_BASE_URL` env var |

## 🎨 Materiales y dimensiones

* Usa siempre dimensiones reales en metros.
* Aplica materiales con color. No dejes nada sin material.
* Para Blender 4.2+, usa `BLENDER_EEVEE_NEXT` en lugar de `BLENDER_EEVEE`.

## ⏱️ Timeout

El socket server (`_axsock.py`) tiene un timeout de **10 segundos** por ejecución de código.
Si necesitas más tiempo para operaciones complejas (rigging, render), aumenta `signal.alarm()`.

---
*Este manual es la autoridad máxima sobre el comportamiento del agente.*
