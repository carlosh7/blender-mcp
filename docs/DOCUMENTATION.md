# blender-mcp-ultra — Documentación Completa

## Visión General

blender-mcp-ultra es un sistema profesional de modelado 3D que integra:
- **Integración AI** con Ollama para crear objetos desde lenguaje natural
- **Motor de modelado** con primitivas avanzadas
- **Motor de texturizado** con 50+ materiales PBR
- **Motor de rigging** con auto-rig para humanoides y cuadrúpedos
- **Motor de animación** con walk cycles, facial, gestures
- **Sistema de personajes** para 5 tipos de criaturas
- **Motor de física** para cloth, fluid, particles
- **Sistema de percepción** para analizar escenas
- **Control por voz** para interacción natural
- **Sistema de referencia** para guiar creaciones
- **Exportación** a múltiples formatos

## Instalación

### Requisitos
- Blender 4.0+
- Python 3.10+
- Ollama (para IA)

### Pasos
1. Descargar el repositorio
2. Ejecutar: `python3 create_addon_zip.py`
3. En Blender: Edit → Preferences → Get Extensions → Install from Disk
4. Seleccionar `/tmp/blender_addon.zip`
5. Activar "blender_mcp_ultra"

## Uso

### Text to 3D
```
En el panel MCP:
1. AI Assistant → Description: "Una silla roja de madera"
2. Click [Create]
3. Blender crea el modelo automáticamente
```

### Voice Control
```
Comandos de voz:
- "Crear un cubo rojo"
- "Eliminar la esfera"
- "Analizar la escena"
- "Exportar modelo"
```

### Scene Analysis
```
En el panel MCP:
1. Perception → [Analyze]
2. Sistema analiza: objetos, materiales, calidad
3. Muestra score: 89/100
```

### Reference Compare
```
1. Cargar imagen de referencia
2. Comparar con escena actual
3. Sistema detecta coincidencias y diferencias
```

## Arquitectura

```
blender-mcp-ultra/
├── addon/
│   ├── core/           # Motores fundamentales
│   ├── organic/        # Sistema orgánico
│   ├── physics/        # Simulación física
│   ├── ai/             # Asistente IA
│   ├── perception/     # Sistema de visión
│   ├── libraries/      # Bibliotecas
│   ├── export/         # Exportación
│   └── ui/             # Panel de usuario
├── tests/              # Suite de tests
└── docs/               # Documentación
```

## API Reference

### AI Integration
```python
from ai.ai_integration import text_to_3d, query_llm

# Crear objeto desde texto
obj = text_to_3d("Una silla roja de madera")

# Consultar LLM
response = query_llm("¿Qué es 2+2?")
```

### Voice Control
```python
from ai.voice_control import execute_voice_command

# Ejecutar comando de voz
result = execute_voice_command("Crear cubo rojo")
```

### Perception
```python
from perception.perception_system import analyze_scene

# Analizar escena
result = analyze_scene()
print(f"Score: {result['summary']['score']}/100")
```

### Physics
```python
from physics.physics_engine import add_cloth, add_rigid_body

# Agregar cloth
add_cloth(obj, preset="cotton")

# Agregar rigid body
add_rigid_body(obj, mass=1.0)
```

### Sculpting
```python
from organic.sculpt_engine import sculpt_face, sculpt_body

# Sculpt cara
face = sculpt_face(head_obj)

# Sculpt cuerpo
body = sculpt_body(torso_obj)
```

## Troubleshooting

### Error: "No module named 'bpy'"
- Solución: Ejecutar dentro de Blender, no fuera

### Error: "Ollama not connected"
- Solución: Verificar que Ollama esté corriendo en localhost:11434

### Error: "register_class already registered"
- Solución: Desactivar y reactivar el addon

### Error: "Socket timeout"
- Solución: Verificar que Blender esté corriendo y el addon activo

## License

MIT License
