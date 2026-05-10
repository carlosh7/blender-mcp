# Modos de interacción — blender-mcp

El servidor soporta 4 modos de interacción, desde el más simple hasta el más avanzado.

---

## Modo A: Terminal / opencode (sin Blender abierto)

**Ideal para:** Generación rápida, integración con check-3d-planner.

```
Tú (terminal) → opencode → MCP server → Blender headless → .glb
```

**Flujo:**
```bash
python server.py --mode standalone
# Desde opencode: "crea una silla plegable"
# Blender genera headless (~3 segundos)
# .glb aparece en models/
```

**Ventajas:** Rápido, no requiere abrir Blender, ideal para lotes.

---

## Modo B: Addon de Blender (chat desde dentro de Blender)

**Ideal para:** Iteraciones rápidas, ver resultados en vivo.

```
Tú (dentro de Blender) → Addon panel → MCP server → Blender ejecuta → ves en vivo
```

**Flujo:**
1. Activas addon en Blender (sidebar → AI)
2. Click "Connect"
3. Escribes en el chat: "crea una lámpara"
4. MCP server recibe, ejecuta script en Blender
5. Ves la lámpara aparecer en el viewport
6. "el pie muy grueso" → se actualiza en vivo

**Ventajas:** Sin cambiar de programa, feedback visual inmediato.

---

## Modo C: Editar proyecto existente

**Ideal para:** Modificar escenas que ya tienes en Blender.

```
Tú abres proyecto → Addon "Capture Scene" → IA analiza → Tú pides cambios
```

**Flujo:**
1. Abres tu proyecto de Blender
2. Click "📷 Capture Scene"
3. El addon envía: lista de objetos + screenshot
4. Yo analizo y te confirmo lo que veo
5. Pides cambios específicos
6. El script modifica solo lo necesario (sin resetear la escena)

**Ventajas:** Trabajas sobre tu escena real, no desde cero.

---

## Modo D: Iteración guiada con Blender GUI

**Ideal para:** Diseño iterativo, ajustes finos.

```
Tú: "crea X" → aparece → "más grande" → cambia → "color rojo" → cambia
```

**Flujo:**
1. `python server.py --mode gui`
2. Blender se abre con interfaz
3. Pides el primer modelo
4. Blender lo dibuja en pantalla
5. Iteras cambios sin cerrar Blender
6. Exportas solo cuando esté perfecto

**Ventajas:** Control total del proceso creativo, ves cada cambio.

---

## Resumen

| Modo | Blender | Velocidad | Ideal para |
|------|---------|-----------|------------|
| A: Terminal | Headless | ⚡ 1-3s | Generación rápida, lotes |
| B: Addon chat | GUI + addon | 🟡 2-5s | Iteraciones desde Blender |
| C: Editar proyecto | GUI + addon | 🟡 3-8s | Modificar escenas existentes |
| D: GUI interactiva | GUI visible | 🟡 3-8s | Diseño iterativo completo |
