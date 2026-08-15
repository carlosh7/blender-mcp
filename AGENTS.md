# blender-mcp — Agent Knowledge (Axiom v3.0 Edition)

Este archivo define las leyes globales para cualquier agente IA operando blender-mcp.

## ⚖️ Reglas de Oro (Inquebrantables)

1. **PERCEPCIÓN PRIMERO**: ANTES de crear CUALQUIER cosa, USA `get_scene_info()` para ver qué existe.
2. **VALIDAR DESPUÉS**: DESPUÉS de crear CADA pieza, USA `validate_object()` para verificar.
3. **VER VISUALMENTE**: DESPUÉS de cada paso, USA `get_viewport_screenshot()` para ver el resultado.
4. **CONECTAR PIEZAS**: Usa `snap_and_parent()` para unir piezas correctamente.
5. **NO BORRAR TODO**: Si algo está mal, CORRIGE solo eso, no borres todo.
6. **MEDIR DISTANCIAS**: Usa `get_bbox()` para verificar tamaños y posiciones.
7. **NO ENTREGAR PRIMITIVAS PURAS**: Todo objeto debe incluir biselado (`apply_professional_finish` / Bevel), sombreado suave (*Shade Auto Smooth*) y volumen 3D real.
8. **USAR MATERIALES PBR REALES**: Asignar siempre materiales procedurales PBR (`create_pbr_wood`, `create_pbr_fabric`, etc.) con mapas de relieve (*Bump/Normal*).
9. **AUTO-DESEMPAQUETADO UV**: Todo objeto generado con `bmesh` debe desdoblarse automáticamente (*Smart UV Unwrapping*).

## 🚫 REGLA ABSOLUTA: NO BLOCKOUT / NO BLOCKING

### Definición
**BLOCKOUT/BLOCKING** = Cualquier objeto que sea solo una primitiva básica (cubo, esfera, cilindro) sin detalles, sin materiales reales, sin biselado, sin formas orgánicas. Es un PLACEHOLDER, no un objeto final.

### Qué SÍ es blockout (PROHIBIDO):
- Cubo sin biselado que representa una silla
- Esfera que representa una cabeza
- Cilindro que representa una pierna
- Cubo escalado que representa una mesa
- Cualquier primitiva sin Details+Materials+Finish

### Qué SÍ es aceptable (REQUERIDO):
- Silla con patas, asiento, respaldo, biselado, madera PBR
- Cabeza con forma orgánica, ojos, nariz, boca, piel PBR
- Pierna con muslo, rodilla, pantorrilla, pie, biselado
- Mesa con tablero, patas, bisagras, madera PBR

### Flujo obligatorio al crear CUALQUIER objeto:
```
1. ANTES de crear:
   - ¿Qué forma REAL tiene este objeto?
   - ¿Qué detalles tiene (biselados, curvas, texturas)?
   - ¿Qué material PBR lleva?

2. DURANTE la creación:
   - USAR bmesh para formas complejas
   - AGREGAR biselado a TODOS los bordes
   - ASIGNAR material PBR real
   - APLICAR Smart UV Unwrap

3. DESPUÉS de crear:
   - ¿Tiene biselado? → Si NO, agregarlo
   - ¿Tiene material PBR? → Si NO, asignarlo
   - ¿Tiene sombreado suave? → Si NO, aplicarlo
   - ¿Se ve como el objeto real? → Si NO, mejorar detalles
```

### Validación anti-blockout:
```python
def is_blockout(obj):
    """Detectar si un objeto es blockout (prohibido)."""
    # Sin biselado = blockout
    # Solo 1 material simple = blockout
    # Primitiva básica sin modificar = blockout
    # Sin sombreado suave = blockout
    # Menos de 10 vértices para objetos complejos = blockout
```

## 🔄 Workflow Obligatorio (para cualquier objeto)

### ANTES de crear:
```
1. get_scene_info()        → ¿Qué hay en la escena?
2. get_spatial_visual()    → ¿Cómo se ve actualmente?
```

### DESPUÉS de cada pieza:
```
1. validate_object()       → ¿La pieza está correcta?
2. get_viewport_screenshot() → ¿Cómo se ve visualmente?
3. verify_connection()     → ¿Está conectada a otra pieza?
```

### DESPUÉS de terminar:
```
1. validate_scene()       → ¿Todo está bien?
2. get_scene_summary()    → Resumen final
3. get_viewport_screenshot() → Ver resultado final
```

## 📋 Herramientas Disponibles (50+)

### Percepción (VER)
| Herramienta | Función |
|-------------|---------|
| `get_scene_info()` | Información de la escena |
| `get_viewport_screenshot()` | Captura del viewport |
| `get_spatial_visual()` | Relaciones espaciales |
| `analyze_scene()` | Análisis completo |

### Validación (VERIFICAR)
| Herramienta | Función |
|-------------|---------|
| `validate_scene()` | Validar toda la escena |
| `validate_object()` | Validar pieza individual |
| `validate_geometry()` | Validar geometría |

### Creación (CONSTRUIR)
| Herramienta | Función |
|-------------|---------|
| `create_object()` | Crear objeto con reglas |
| `create_collection()` | Crear colección |
| `snap_and_parent()` | Conectar piezas |

### Herramientas Avanzadas
| Herramienta | Función |
|-------------|---------|
| `get_object_anchors()` | Obtener anclas de objeto |
| `apply_symmetry()` | Aplicar simetría |
| `fix_normals()` | Corregir normales |
| `search_assets()` | Buscar assets |
| `generate_3d()` | Generar 3D |

## 🚫 Lo que NO debes hacer

1. **NO borres todo** — Corrige solo lo que está mal
2. **NO crees sin verificar** — Siempre valida después
3. **NO asumas posiciones** — Mide antes de crear
4. **NO ignores errores** — Valida cada pieza

## 📊 Métricas de Éxito

| Métrica | Objetivo |
|---------|----------|
| **Errores por objeto** | 0 |
| **Piezas conectadas** | 100% |
| **Calidad visual** | > 90/100 |
| **Tiempo por objeto** | < 5 min |

---
*Este manual es la autoridad máxima sobre el comportamiento del agente.*
