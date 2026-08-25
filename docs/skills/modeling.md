# Skill: Modelado con blender-mcp-ultra

Recetas probadas E2E (cada una ejecutada y validada en Blender 5.1). Tools: 147 en total.

## Reglas de oro

1. `scene.get_info` ANTES de crear; `scene.query` para nombres exactos.
2. Los índices de malla MUEREN tras cualquier edición → `mesh.get_topology` fresco antes de cada operación.
3. `object.create` devuelve el nombre FINAL (Blender puede renombrar `Cube` → `Cube.001`).
4. Los booleanos dejan slots de material `None`: si algo falla con `NoneType`, revisa materiales.

## Receta: mesa por extrusión (componentes, no primitivas escaladas)

```
1. object.create {type: "MESH", name: "Mesa"}          # mesh vacío
2. execute_code: bpy.ops.mesh.primitive_cube_add()     # primitiva base real
3. mesh.get_topology {object_name}                     # → caras con normal/centro
4. mesh.extrude_faces {face_indices: [top], thickness} # patas/tapa
5. mesh.inset_faces  {face_indices, thickness, depth}  # paneles
6. mesh.bevel_edges  {edge_indices, width, segments}   # romper aristas vivas
7. mesh.recalc_normals {object_name}
8. material.create + material.assign                   # PBR siempre
```

## Receta: forma orgánica (bmesh vía execute_code)

Para perfiles revolucionados (tazas, lámparas, botellas): construye el perfil
`(radio, z)` y revoluciona 64-96 segmentos con `bmesh`; cierra con
`remove_doubles` + `recalc_face_normals`. Ejemplo completo validado: taza con
asa (toro + boolean EXACT) y lámpara Luxo articulada (ver historial de sesión).

## Biselado y sombreado (obligatorio anti-blockout)

- Modificador BEVEL (width ~0.001-0.002, segments 2-3, limit ANGLE 45-50°).
- `p.use_smooth = True` en todos los polígonos.
- `bpy.ops.uv.smart_project(angle_limit=66°, island_margin=0.02)`.

## Validación

- `scene_utils.mesh_analysis {object_name}` → verts/faces/tris.
- Screenshot del viewport en shading MATERIAL antes de dar por bueno el modelo.
