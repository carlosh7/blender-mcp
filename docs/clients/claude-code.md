# Claude Code — Integración

`blender-mcp-ultra` se conecta a Claude Code vía **MCP stdio** (transporte
estándar). El gateway es `mcp_server.py` (223 tools: 6 base + registry dinámico).

## Requisitos

- Blender 4.2+ (o 5.x) con el addon `blender_mcp_ultra.zip` instalado y el
  socket activo (panel N → blender-mcp → Connect, puerto 9876)
- Python 3.10+ con `pip install -e .` en el repo (o `pip install blender-mcp-ultra`)
- Claude Code CLI instalado

## Registro (un solo comando)

```bash
claude mcp add blender -- python /ruta/a/blender-mcp/mcp_server.py
```

Con scope de usuario (disponible en todos tus proyectos):

```bash
claude mcp add --scope user blender -- python /ruta/a/blender-mcp/mcp_server.py
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

Claude Code invocará las tools `scene.*`, `render.*`, `export.*`, etc.

## Notas

- El gateway se comunica con Blender por socket local `localhost:9876` —
  nunca por red.
- Si el socket no responde, las tools devuelven un error claro: abre Blender
  y pulsa **Connect** en el panel del addon.
- Para exponer más tools del registry dinámicamente, el gateway las descubre
  al arrancar (ver log: `Starting MCP Server (N tools...)`).
- Alternativa con SSE (para clientes remotos): `python mcp_server.py --sse`
  y apunta el cliente a `http://localhost:9879/sse`.
