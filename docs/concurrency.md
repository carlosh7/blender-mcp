# Modelo de concurrencia

Cómo maneja blender-mcp-ultra las llamadas simultáneas, y qué límites son
arquitectónicos (no bugs).

## Modo GUI (Blender con interfaz)

```
cliente A ─┐
cliente B ─┼─ thread por cliente (socket :9876)
cliente C ─┘        │
                    ▼  bpy.app.timers (first_interval=0)
        HILO PRINCIPAL de Blender — ejecuta los comandos en serie
```

- Cada conexión abre un hilo de red; **todo acceso a bpy se serializa al
  hilo principal** vía `bpy.app.timers` (bpy no es thread-safe).
- Las respuestas vuelven en el modo del cliente (framed v2 o legacy).

## Modo headless (`blender -b`, CI/host)

El hilo principal está ocupado por el bucle bloqueante `serve_forever()`,
así que **no hay timers**: los comandos se ejecutan directamente en el
hilo principal, un cliente cada vez. Cuando un cliente queda inactivo 0.5s
se cede el turno al siguiente (round-robin justo; el gateway reconecta de
forma transparente).

**Límite arquitectónico:** dos clientes no ejecutan comandos a la vez en
headless — Blender no ofrece forma de procesar timers mientras el bucle
bloquea. Es una decisión de seguridad (bpy serializado) más que una
carencia del protocolo.

## Lado gateway

- `blender_connection` serializa peticiones con un lock por conexión: las
  llamadas MCP concurrentes no cruzan respuestas. Una operación larga
  (render, bake) bloquea a las demás **de la misma conexión de gateway**;
  clientes distintos tienen conexiones propias.

## Operaciones largas: usa jobs

Los renders no bloquean: `render_start` devuelve un `job_id` y se consulta
con `render_status` / `render_list` (progreso vía `poll_events`). El mismo
patrón sirve para simulaciones horneadas (`physics.bake`).

## Multi-agente

Varios agentes sobre un mismo Blender deben coordinarse con el lock de
escena advisory (`scene_lock(action='acquire')`) para comandos mutadores;
el lock lo respeta el addon (`execute_code`, `tool`, `create_object`,
`cleanup_scene`).

## Multi-instancia

¿Real parallelismo? Arranca otra instancia de Blender en otro puerto
(`BLENDER_MCP_SOCKET_PORT`) y apunta un gateway distinto con `BLENDER_PORT`
— ver [docs/multi-instance.md](multi-instance.md).
