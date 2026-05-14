# Arquitectura Técnica: Axiom Precision Engine v2.0

Axiom v2.0 utiliza una arquitectura de microservicios desacoplada para garantizar estabilidad, seguridad y precisión.

## 🏗️ Diagrama de Flujo
1. **Agent Host (Trinity)**: Procesa el lenguaje natural y genera planes de ingeniería.
2. **AST Validator**: Filtra el código generado antes de enviarlo.
3. **MCP Server**: Expone las herramientas de Blender al Agente.
4. **Precision Socket**: Puente TCP (9876) que ejecuta comandos dentro del thread principal de Blender.
5. **Oracle (QC)**: Valida la geometría resultante tras la ejecución.

## 🛡️ Capa de Seguridad (AxiomValidator)
Implementamos un validador de **Abstract Syntax Tree (AST)** en `agent_host.py` que analiza cada bloque de código Python. 
*   **Whitelist**: Permite `bpy`, `mathutils`, `math`, `json`.
*   **Blacklist**: Bloquea `os`, `sys`, `subprocess`, `exec`, `eval`.
Cualquier intento de violación de seguridad dispara un bloqueo inmediato y un reporte al log de auditoría.

## 📐 Motor de Ensamblaje (Assembly Engine v2.0)
El sistema de 27 anclas utiliza la caja delimitadora (Bounding Box) de los objetos para generar una matriz de puntos de control:
*   Nomenclatura: `A_[MIN|CENTER|MAX]_[MIN|CENTER|MAX]_[MIN|CENTER|MAX]`.
*   Ejemplo: `A_MIN_CENTER_MIN` representa el punto medio de la base frontal de un objeto.
Esto permite un snapping determinista sin errores de flotación (Z-fighting).

## 🔮 El Oráculo (Detección de Colisiones)
El Oráculo utiliza `mathutils.bvhtree` para construir árboles de jerarquía de volúmenes en tiempo real. 
*   **Overlaps**: Detecta si las caras de dos mallas se intersectan.
*   **Epsilon Checks**: Valida si hay huecos (gaps) no deseados entre componentes que deberían estar en contacto físico.

## 🔄 Transacciones Atómicas
Todas las ejecuciones de código IA están envueltas en un wrapper de `undo_push`. 
*   Si el Oráculo detecta una colisión crítica tras un ensamble, el sistema invoca un `bpy.ops.ed.undo()` automático.
*   La escena de Blender se mantiene siempre en un estado "Válido" de ingeniería.
