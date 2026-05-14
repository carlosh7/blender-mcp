# 💎 AXIOM Precision Engine v2.0

**Axiom v2.0** es un ecosistema de ingeniería audiovisual autónomo para Blender. No es un generador de bocetos; es un motor de ensamblaje determinista diseñado para cumplir con estándares CNC e industriales mediante integración MCP (Model Context Protocol).

## 🚀 Características Principales (Axiom v2.0)

### 1. Ensamblaje Determinista (27-pt Anchors)
Axiom abandona las coordenadas manuales. Utiliza un sistema de **27 puntos de anclaje globales** (A_MIN_CENTER_MAX) para garantizar que cada pieza encaje con precisión milimétrica.

### 2. Trinity: El Cerebro Autónomo
El Agente Trinity opera bajo un **Bucle de Reflexión**:
*   **PLAN**: Diseño detallado antes de la ejecución.
*   **ACT**: Construcción basada en anclas.
*   **SCAN**: Validación mediante Scanner v0.4.0 (Blueprints JSON).
*   **FIX**: Autocorrección inmediata ante desviaciones >0.001mm.

### 3. El Oráculo (Validación Espacial)
Integración de detección de colisiones basada en **BVH (Bounding Volume Hierarchy)**. El Oráculo detecta:
*   Intersecciones críticas de mallas.
*   **Z-Fighting**: Solapamientos coplanares destructivos.
*   **Stability**: Detección de objetos flotantes sin anclaje.

### 4. Blindaje de Seguridad AST
Ejecución de código Python protegida. El validador de **Árbol de Sintaxis Abstracta (AST)** bloquea cualquier operación no autorizada fuera de la API de Blender, garantizando un entorno de ejecución seguro y reversible (Atomic Undo).

## 📦 Instalación Atómica (GitHub ZIP)

Este repositorio está diseñado para ser instalado directamente en Blender sin configuración externa:

1.  Descarga el código como `.zip` desde el botón **Code > Download ZIP** de GitHub.
2.  En Blender: `Edit > Preferences > Add-ons > Install...`
3.  Selecciona el archivo descargado.
4.  **Auto-Install**: Al activar el addon, Axiom instalará automáticamente todas las dependencias (`mcp`, `fastmcp`, `uvicorn`, etc.) vía `pip` de forma silenciosa.

## 🛠️ Stack Tecnológico
*   **Core**: Python 3.10+ / Blender API (bpy)
*   **Protocol**: MCP (Model Context Protocol)
*   **Security**: AST Static Analysis
*   **Physics**: BVH Collision Trees
*   **Generative**: Rodin (Hyper3D) / Hunyuan3D Bridge

---
*Desarrollado por CarlosH para Ingeniería Audiovisual de Alta Fidelidad.*
