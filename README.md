# blender-mcp

Controla Blender desde cualquier LLM (IA) mediante chat interno o protocolo MCP.

## Cómo funciona

El LLM recibe **6 herramientas** para controlar Blender:

| Herramienta | Para qué |
|-------------|----------|
| `search_api_docs(query)` | Buscar la API correcta en la documentación de Blender |
| `get_python_api_docs(topic)` | Leer documentación detallada de una función |
| `execute_blender_code(code)` | Ejecutar código Python en Blender |
| `get_scene_info()` | Inspeccionar el estado de la escena |
| `get_viewport_screenshot()` | Ver el resultado visual |
| `snap_and_parent(...)` | Ensamblaje determinista por anclas (27 pts) |

**Regla de oro**: el LLM SIEMPRE busca en la documentación antes de ejecutar código. No inventa APIs.

## Instalación

1. Descarga el `.zip` desde GitHub Releases
2. En Blender: `Edit > Preferences > Add-ons > Install...`
3. Activa "AXIOM Precision Engine"
4. Abre el panel Axiom (tecla N en 3D View > Axiom tab)
5. En Scene Properties > Axiom Engine Config, selecciona un modelo de IA

## Uso

Escribe en el chat de Blender (panel Axiom):

```
pon un cilindro rojo de 2 metros
```

La IA busca en la documentación, encuentra la API correcta, genera el código y lo ejecuta.

También puedes conectar opencode, Claude Desktop o Cursor vía MCP.

## Documentación offline (opcional)

Para búsqueda más precisa, ve a **Scene Properties > Axiom Engine Config > Documentación API** y haz clic en "Download RST Docs" (1.3 MB, descarga única).

## Stack

- **Core**: Python / Blender API (bpy)
- **Protocol**: MCP (Model Context Protocol)
- **Docs**: 2,062 RST + TF-IDF search engine
- **Assembly**: 27-anchor deterministic snapping
- **Validation**: BVH collision detection
