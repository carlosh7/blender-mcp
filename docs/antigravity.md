# Antigravity Integration (HTTP Bridge)

Conecta blender-mcp con [Antigravity](https://antigravity.dev) y cualquier cliente HTTP via REST API.

## Cómo funciona

El `http_bridge.py` expone una API REST en el puerto **9877** para clientes HTTP.

## Iniciar el bridge

```bash
# Automático (con el MCP server)
python server.py --mode all

# O standalone
python http_bridge.py
```

## Endpoints

### GET /api/health
```json
{
  "status": "ok",
  "version": "0.8.0",
  "ai_state": "connected",
  "models_dir": "/home/.../models",
  "models_count": 5
}
```

### GET /api/providers
```json
{
  "found": true,
  "current_model": "anthropic/claude-sonnet-4",
  "current_provider": "anthropic",
  "providers": [
    {"id": "anthropic", "name": "Anthropic Claude", "connected": true}
  ]
}
```

### POST /api/chat
```json
// Request
{ "message": "crea una esfera roja" }

// Response
{ "status": "queued", "message_id": "uuid-123" }

// Poll
GET /api/chat/status?message_id=uuid-123
```

### POST /api/generate
```json
// Request
{ "model_type": "chair-folding", "name": "mi_silla" }

// Response
{ "success": true, "file": "/path/to/model.glb", "size_bytes": 4096 }
```

### POST /api/set-model
```json
{ "model": "deepseek/deepseek-chat" }
```

## Integración con Antigravity

1. Asegúrate de que `http_bridge.py` esté corriendo (puerto 9877)
2. Configura Antigravity para apuntar a `http://localhost:9877/api/`
3. Usa el endpoint `/api/chat` para enviar mensajes
4. El agente autónomo procesará la solicitud y generará la respuesta

## CORS

Todos los endpoints tienen CORS habilitado (`Access-Control-Allow-Origin: *`).
