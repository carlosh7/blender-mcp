# blender-mcp-ultra — Guía de Uso Rápido

## Instalación (2 minutos)

```bash
# 1. Clonar repositorio
git clone https://github.com/carlosh/blender-mcp-ultra.git
cd blender-mcp-ultra

# 2. Crear zip del addon
python3 create_addon_zip.py

# 3. En Blender: Edit → Preferences → Get Extensions → Install from Disk
# Seleccionar: /tmp/blender_addon.zip
# Activar: blender_mcp_ultra
```

## Uso Básico

### Text to 3D
```
En panel MCP:
1. AI Assistant → Description: "Una silla roja de madera"
2. Click [Create]
→ Blender crea el modelo automáticamente
```

### Voice Control
```
Comandos:
- "Crear cubo rojo"
- "Eliminar esfera"
- "Analizar escena"
- "Exportar modelo"
```

### Scene Analysis
```
En panel MCP:
1. Perception → [Analyze]
→ Sistema analiza: objetos, materiales, calidad
→ Muestra score: 89/100
```

## Features

| Feature | Estado | Descripción |
|---------|--------|-------------|
| AI Integration | ✅ | Ollama phi3:mini |
| Text→3D | ✅ | Crea desde texto |
| Voice Control | ✅ | Comandos de voz |
| Scene Analysis | ✅ | Analiza escena |
| Quality Check | ✅ | Verifica calidad |
| Animation | ✅ | Keyframes |
| Physics | ✅ | Cloth, Rigid Body |
| Character Gen | ✅ | Humanoid |
| Building Gen | ✅ | Office |
| Export | ✅ | FBX, OBJ |

## Documentación

- [Guía completa](docs/DOCUMENTATION.md)
- [API Reference](docs/DOCUMENTATION.md#api-reference)
- [Troubleshooting](docs/DOCUMENTATION.md#troubleshooting)
