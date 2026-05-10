# Integración con check-3d-planner

Cómo usar blender-mcp para generar modelos para el editor de planos 3D de eventos.

---

## Modo check

```bash
python server.py --mode check --check-path /ruta/a/check-3d-planner/public/models
```

En este modo, cada modelo generado se copia automáticamente al directorio correcto.

---

## Flujo de trabajo

```
1. Inicias el server en modo check
2. Desde opencode: "genera una silla ejecutiva para el editor de planos"
3. MCP server genera el .glb y lo copia a public/models/
4. El modelo ya está disponible en el editor 3D
5. Solo queda agregar la entrada en GLTF_MODELS en Object3D.tsx
```

---

## Registro de modelos

Los modelos GLTF se registran en `Object3D.tsx`:

```typescript
const GLTF_MODELS: Record<string, string> = {
  'chair-folding': '/models/chair-folding.glb',
  'chair-executive': '/models/chair-executive.glb',
  // ... agregar aquí
}
```

El MCP server puede generar automáticamente este código si se lo pides:

```
"agrega la entrada GLTF_MODELS para el modelo que acabo de crear"
```

---

## Catálogo actual

Ver `list-models` en el servidor para ver todos los modelos disponibles.
