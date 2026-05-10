# Plan: Selector de modelos IA en Blender

> Fecha: 2026-05-10
> Proyecto: blender-mcp v0.6.1
> Objetivo: Listar modelos de proveedores conectados a opencode y seleccionarlos desde Blender

---

## 1. Arquitectura

```
Blender Addon                  HTTP Bridge                    opencode config
┌─────────────┐    GET/POST    ┌──────────────┐    Lee       ┌──────────────────┐
│ Selector de  │ ───────────→ │ /api/models   │ ──────────→ │ ~/.config/opencode│
│ modelos con  │ ←─────────── │ /api/providers│ ←────────── │ /opencode.json    │
│ scroll+búsq. │    JSON      │              │             └──────────────────┘
└─────────────┘               │ /api/set-model│             ┌──────────────────┐
                              │              │ ──────────→ │ Escribe el nuevo │
                              │              │             │ modelo en config │
                              └──────────────┘             └──────────────────┘
```

---

## 2. Endpoints del HTTP Bridge

| Endpoint | Método | Qué hace |
|----------|--------|----------|
| `/api/providers` | GET | Lee opencode config y devuelve qué proveedores tienen API key configurada |
| `/api/models?provider=anthropic` | GET | Consulta los modelos disponibles de ese proveedor |
| `/api/models?provider=openrouter` | GET | Consulta OpenRouter API pública para listar 300+ modelos |
| `/api/set-model` | POST | Cambia el modelo en el archivo de configuración |

### Respuesta ejemplo de `/api/providers`

```json
{
  "providers": [
    {"id": "anthropic", "name": "Anthropic", "connected": true, "model_count": 8},
    {"id": "openai", "name": "OpenAI", "connected": true, "model_count": 12},
    {"id": "openrouter", "name": "OpenRouter", "connected": true, "model_count": 300},
    {"id": "deepseek", "name": "DeepSeek", "connected": false, "model_count": 0}
  ],
  "current_model": "anthropic/claude-sonnet-4-5",
  "config_file": "/home/carlosh/.config/opencode/opencode.json"
}
```

### Respuesta ejemplo de `/api/models?provider=openrouter`

```json
{
  "provider": "openrouter",
  "models": [
    {"id": "anthropic/claude-sonnet-4-5", "name": "Claude Sonnet 4.5"},
    {"id": "openai/gpt-4o", "name": "GPT-4o"},
    {"id": "deepseek/deepseek-chat", "name": "DeepSeek Chat"},
    {"id": "mistralai/mistral-large", "name": "Mistral Large"},
    "..."
  ],
  "total": 312,
  "page": 1,
  "page_size": 50
}
```

---

## 3. Interfaz en Blender

### Panel en Properties > Scene > AI Config

```
┌──────────────────────────────────┐
│ 🔍 [Buscar modelo...]            │ ← texto libre para filtrar
├──────────────────────────────────┤
│ Proveedores conectados:          │
│                                  │
│ 📡 Anthropic (8 modelos)         │ ← sección colapsable
│   ○ claude-sonnet-4-5  ← actual  │ ← radio button
│   ○ claude-haiku-4-5             │
│   ○ claude-opus-4-5              │
│   ...                            │
│                                  │
│ 📡 OpenAI (12 modelos)           │
│   ○ gpt-4o                       │
│   ○ gpt-4o-mini                  │
│   ...                            │
│                                  │
│ 📡 OpenRouter (300+ modelos)     │
│   [Cargar más...]                │ ← paginación
│                                  │
├──────────────────────────────────┤
│ [Aplicar modelo]                 │ ← guarda en config
└──────────────────────────────────┘
```

### Componentes Blender a crear

| Clase | Tipo | Función |
|-------|------|---------|
| `MCP_UL_Models` | UIList | Lista con scroll de modelos |
| `OP_FetchProviders` | Operator | Obtiene proveedores del server |
| `OP_FetchModels` | Operator | Obtiene modelos de un proveedor |
| `OP_SetModel` | Operator | Cambia el modelo (ya existe) |
| `OP_SearchModels` | Operator | Filtra modelos por texto |

---

## 4. Archivos a modificar

| Archivo | Cambio |
|---------|--------|
| `http_bridge.py` | + `/api/providers`, `/api/models?provider=`, `/api/set-model` |
| `addon/__init__.py` | + Panel de selección con UIList, buscador, botones |
| `config.py` | + Función `read_opencode_config()`, `write_opencode_config()` |
| `docs/MODEL_SELECTOR.md` | (nuevo) Documentación del selector |

---

## 5. Tiempo estimado

| Tarea | Tiempo |
|-------|--------|
| Endpoint `/api/providers` (leer config) | 🟢 30min |
| Endpoint `/api/models` (OpenRouter API pública) | 🟡 1h |
| Endpoint `/api/set-model` (escribir config) | 🟢 30min |
| UIList con scroll en Blender | 🟡 2h |
| Buscador/filtro de modelos | 🟡 1h |
| Paginación para OpenRouter (300+) | 🟡 1h |
| Pruebas y ajustes | 🟡 1h |
| **Total** | **~7h** |

---

## 6. Notas técnicas

- **OpenRouter API pública**: `https://openrouter.ai/api/v1/models` — no requiere API key para listar modelos
- **Config de opencode**: Se lee de `~/.config/opencode/` o `Check/opencode.json`
- **Providers sin API pública**: No podemos listar modelos de Anthropic/OpenAI sin sus API keys (no las tenemos en el server). Solución: mostrar una lista curada de modelos conocidos para cada proveedor
- **OpenRouter**: API pública, podemos listar TODOS los modelos sin necesidad de key
