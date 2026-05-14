# blender-mcp — Agent Knowledge (Axiom v2.0 Edition)

Este archivo define las leyes globales para cualquier agente IA operando el Axiom Precision Engine.

## ⚖️ Reglas de Oro (Inquebrantables)
1.  **Cero Coordenadas Manuales**: Queda terminantemente prohibido mover objetos usando `obj.location = (x, y, z)`. Se debe usar siempre el sistema de anclas `snap_and_parent` o `snap_to_anchor`.
2.  **Protocolo de Reflexión**: Tras cada acción de ensamblaje, el agente DEBE ejecutar `validate_geometry` y `get_model_blueprint` para confirmar el resultado.
3.  **Seguridad AST**: El código generado será auditado. No intentes importar módulos de sistema (`os`, `sys`). Usa únicamente `bpy`.
4.  **Estándar de Nomenclatura de Anclas**: 
    *   Formato: `A_X_Y_Z` donde X,Y,Z pueden ser `MIN`, `CENTER` o `MAX`.
    *   Punto Pivote por defecto: `A_CENTER_CENTER_CENTER`.

## 🏗️ Workflow de Ingeniería
1.  **Scan**: Analizar el entorno usando `get_objects_summary`.
2.  **Blueprint**: Obtener las anclas del objeto objetivo con `get_model_blueprint`.
3.  **Assembly**: Ejecutar el snap usando la herramienta `snap_and_parent`.
4.  **Oracle**: Validar colisiones con `validate_geometry`.
5.  **Reflect**: Si el Oráculo reporta `❌ COLISIÓN`, retroceder y ajustar anclas.

## 🎨 Estética y Materiales
*   Usa siempre dimensiones reales en metros.
*   Aplica materiales basados en IOR real cuando sea posible (especialmente para equipos AV).
*   Mantén la jerarquía (parenting) limpia para facilitar ajustes posteriores del usuario.

---
*Este manual es la autoridad máxima sobre el comportamiento del agente.*
