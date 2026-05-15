# blender-mcp — Agent Knowledge (Axiom v3.0 Edition)

Este archivo define las leyes globales para cualquier agente IA operando blender-mcp.

## ⚖️ Reglas de Oro (Inquebrantables)
1.  **Buscar antes de ejecutar**: Antes de escribir CUALQUIER código bpy, llama a `search_api_docs(consulta)` para encontrar la API correcta. No inventes nombres de funciones.
2.  **Cero Coordenadas Manuales**: No uses `obj.location = (x, y, z)`. Usa siempre `snap_and_parent` o `snap_to_anchor`.
3.  **Validar después de ensamblar**: Tras cada snap, ejecuta `validate_geometry()` para detectar colisiones.
4.  **Estándar de Nomenclatura de Anclas**: Formato `A_X_Y_Z` donde X,Y,Z pueden ser `MIN`, `CENTER` o `MAX`.

## 🏗️ Workflow
1.  **Consultar**: `search_api_docs(query)` para aprender la API correcta.
2.  **Inspeccionar**: `get_scene_info()` para conocer el estado actual.
3.  **Ejecutar**: `execute_blender_code(code)` con el código correcto (basado en docs).
4.  **Ensamblar**: `snap_and_parent()` con sistema de 27 anclas.
5.  **Validar**: `validate_geometry()` para verificar colisiones.

## 🎨 Materiales y dimensiones
*   Usa siempre dimensiones reales en metros.
*   Aplica materiales con color. No dejes nada sin material.

---
*Este manual es la autoridad máxima sobre el comportamiento del agente.*
