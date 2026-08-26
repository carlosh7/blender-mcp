# Guía de construcción de escenas para agentes

> Referencia rápida para construir escenas creíbles con blender-mcp-ultra.
> Léela antes de una escena grande; evita los errores más comunes.

## Reglas de oro

1. **Dimensiona con `spatial.dimensions`** antes de crear: una mesada mide 0.9m
   de alto, una puerta 2.1×0.9m, una taza 0.1m. Escenas "de juguete" delatan
   escala incorrecta.
2. **Coloca con `object.place_bottom` / `object.snap_to`**, nunca con
   `object.transform` directo: el origen del objeto rara vez coincide con su base.
3. **Verifica sin render**: `camera.check` (¿está en cuadro?) y
   `spatial.floorplan` (¿cómo está distribuida la escena?) antes de un render caro.
4. **Itera con `render.preview`** (EEVEE 30-50%) y reserva Cycles para el final.
5. **Marca y compara**: `scene.mark` antes de un bloque de trabajo →
   `scene.diff` después para saber exactamente qué cambió.
6. **Limpia al terminar**: `scene.cleanup(dry_run=True)` para auditar,
   `dry_run=False` para ejecutar. Los duplicados `.001` y empties de test
   se acumulan rápido en sesiones largas.
7. **Inspecciona la topología** (`inspect.topology`) antes de exportar: ngons,
   UV faltantes o escala sin aplicar rompen pipelines de juego/impresión.

## Flujo recomendado

```
scene.preset(name='estudio')            → entorno base
spatial.dimensions(search='silla')      → tamaños reales
object.create(...) × N                  → geometría
object.place_bottom / spatial.stack     → colocación exacta
material_pbr(...)                       → materiales
scene.mood(mood='cinematic')            → iluminación
camera.set_framing + camera.check       → encuadre verificado
render.preview(scale=30)                → iteración rápida
render.render                           → final
scene.cleanup(dry_run=False)            → dejar limpio
```

## Errores comunes

| Síntoma | Causa | Fix |
|---|---|---|
| El objeto "flota" o se hunde | origen ≠ base | `object.place_bottom(z=0)` |
| Render falla "no camera" | `scene.camera=None` | `camera.set_active` + `camera.check` |
| Escena con cientos de objetos fantasma | tests acumulados | `scene.cleanup(dry_run=False)` |
| Física no simula en headless | caché sin hornear | `physics.bake(frame_end=N)` |
| La sim repite el estado viejo | caché obsoleta | `physics.free_cache()` y re-hornear |
| Materiales se ven planos | sin bump/roughness variación | `material_pbr` (incluye bump) |
| No encuentro la tool que necesito | 239 tools | `tools.search(query='...')` |
