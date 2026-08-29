# Claude Code — Integración

`blender-mcp-ultra` se conecta a Claude Code vía **MCP stdio** (transporte
estándar). El gateway canónico es `mcp_server.py` — **245 tools** (6 base +
239 del registry), que se registran siempre aunque Blender no esté abierto
todavía; ejecutan en cuanto lo abras.

## Requisitos

- Blender 4.2+ (o 5.x) con el addon `blender_mcp_ultra.zip` instalado
  (el socket en `:9876` arranca solo al habilitar el addon; también puedes
  pulsar **Connect** en el panel N)
- El gateway instalado: `pip install blender-mcp-ultra` (provee el comando
  `blender-mcp-server`) o un checkout del repo con `pip install -e .`
- Claude Code CLI instalado

## Registro (un solo comando)

```bash
claude mcp add blender -- blender-mcp-server
```

Si instalaste desde el repo en lugar de PyPI:

```bash
claude mcp add blender -- python /ruta/a/blender-mcp/mcp_server.py
```

Con scope de usuario (disponible en todos tus proyectos):

```bash
claude mcp add --scope user blender -- blender-mcp-server
```

Verifica con:

```bash
claude mcp list
```

## Uso

Dentro de una sesión de Claude Code, simplemente pide:

```
> Crea una escena con una mesa de madera, una taza de café y una lámpara
> Renderiza la escena en Cycles a 1080p
> Exporta la escena a glTF para web
```

Claude Code invocará las tools `scene_*`, `render_*`, `export_*`, etc.

## Notas

- **El orden de arranque no importa**: las tools se registran leyendo el
  registry local, y la ejecución reconecta al socket de Blender por llamada.
  Si una tool se llama con Blender cerrado, devuelve un error claro y
  funciona en cuanto lo abras — sin reiniciar nada.
- El gateway se comunica con Blender por socket local `localhost:9876` —
  nunca por red. Variables opcionales: `BLENDER_HOST`, `BLENDER_PORT`,
  `BLENDER_TOKEN` (si configuraste token en el addon).
- Alternativa con SSE (para clientes remotos): `python mcp_server.py --sse`
  y apunta el cliente a `http://localhost:9879/sse`.
