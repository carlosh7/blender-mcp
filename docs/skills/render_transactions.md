# Skill: Iluminación, render y transacciones

## Iluminación

```
light.create {type: "AREA", location, energy}
light.three_point {}                       # esquema clásico completo
```

Spot con objetivo exacto: crea el spot y orienta con
`(-direccion).to_track_quat("Z","Y")` (los lights emiten por -Z):

```python
d = (target - lamp_head).normalized()
spot.rotation_euler = (-d).to_track_quat("Z", "Y").to_euler()
```

## Render sin bloquear (jobs)

```
render.render_bg {filepath: "/tmp/r_", engine: "BLENDER_EEVEE_NEXT",
                  samples: 32, resolution: [1920, 1080], frame: 1}
→ {job_id}
render.job_status {job_id}     # running/done/error + files[]
```

- El job renderiza en una instancia `blender -b` aparte: la GUI sigue viva.
- Si la escena no tiene cámara activa, se asigna la primera automáticamente.
- EEVEE headless requiere GPU/EGL; si falla, usa CYCLES.

## Render blocking (previews rápidas)

```
render.render_still {filepath, engine, samples: 16, resolution: [640, 480]}
```

## Transacciones (explora sin miedo)

```
scene_snapshot {label: "antes"}     # guarda copia completa
... experimentos destructivos ...
scene_restore {label: "antes"}      # vuelve al estado exacto
scene_snapshots {}                  # lista disponibles
```

⚠ `scene_restore` abre el .blend guardado: las referencias Python previas
mueren; re-consulta la escena después.

## Multi-agente

```
scene_lock {action: "acquire", token: "agente-A"}   # excluye a otros
execute_code {..., lock_token: "agente-A"}          # dueño del lock
scene_lock {action: "release", token: "agente-A"}
```

Comandos sujetos a lock: `execute_code`, `tool`, `create_object`, `cleanup_scene`.
