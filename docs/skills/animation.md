# Skill: Animación y física

Recetas validadas en Blender 5.1 (acciones ranuradas 4.4+/5.x soportadas).

## Keyframes en canales concretos

```
animation.fcurve_set_key {object_name, data_path: "location", index: 2,
                          frame: 1, value: 0.5}
animation.fcurve_set_key {..., frame: 30, value: 1.5}
animation.fcurve_info {object_name}          # verifica keys reales
```

⚠ `value` se aplica DESPUÉS de insertar (el insert usa el valor actual del canal).

## Drivers

```
animation.driver_add {object_name, data_path: "scale", index: 0,
                      expression: "1 + frame / 100",
                      driver_vars: {"otro": "Objeto@location"}}
```

## Constraints

```
animation.constraint_add {object_name, type: "TRACK_TO", target: "Camera",
                          props: {track_axis: "TRACK_NEGATIVE_Z", up_axis: "UP_Y"}}
```

## Shape keys

```
animation.shape_key_add {object_name, name: "Squash"}     # crea Basis si falta
animation.shape_key_set {object_name, name: "Squash", value: 0.7,
                         move_verts: {"0": [0, 0, -0.1]}}
```

## Física

```
physics.rigidbody_add {object_name, body_type: "ACTIVE", mass: 2.0}   # cae
physics.rigidbody_add {object_name: "Suelo", body_type: "PASSIVE"}    # obstáculo
physics.collision_add {object_name, bounce: 0.3}
physics.cloth_add {object_name}
physics.force_field_add {kind: "WIND", strength: 5.0, location: [...]}
physics.bake_rigidbody {frames: 50}     # bloquea unos segundos
```

⚠ En Blender 5.x el rebote de colisión vive en `damping_factor` (inverso) —
la tool lo traduce por ti.
