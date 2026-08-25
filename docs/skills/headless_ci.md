# Skill: Headless y CI

## Servidor sin GUI (desbloqueado en fase 1)

Sin GUI, `bpy.app.timers` nunca dispara → el modo threaded no sirve. Usar el
servidor bloqueante:

```bash
blender -b --factory-startup --python - <<'EOF'
import sys
sys.path.insert(0, "/ruta/al/repo/addon")
import _axsock
_axsock.serve_forever(port=9876)   # no retorna
EOF
```

- `ping`, `execute_code`, `tool` (¡los 147!), `list_tools` funcionan igual.
- `get_viewport_screenshot` NO (no hay viewport).
- Los handlers corren en el hilo principal: bpy es seguro.

## Para CI (GitHub Actions)

1. Lanzar Blender headless con el script de arriba como servicio de fondo.
2. Esperar puerto 9876 (`nc -z localhost 9876`).
3. `pytest tests/` — los e2e de socket dejan de saltarse.
4. `pkill blender` en cleanup.

## Errores comunes → remediación

| Error | Causa | Fix |
|---|---|---|
| `No module named 'src'` | falta la RAÍZ del repo en sys.path (no `src/`) | insertar el padre de `src/` |
| `NoneType has no attribute 'name'` | slot de material None (boolean) o cámara ausente | limpiar slots / asignar scene.camera |
| `keyword "faces" is invalid` (bmesh 5.x) | `extrude_face_region` usa `geom` | ya manejado en mesh_edit |
| `'Action' object has no attribute 'fcurves'` | acciones ranuradas 4.4+ | ya manejado (channelbag) |
| `escena bloqueada por otro agente` | lock activo | `scene_lock acquire` con tu token |
