"""
auto_process.py — Procesa la cola de chat dentro de Blender.
Timer que cada 0.5s revisa mensajes y los envía al LLM configurado.
Sin procesos externos. Sin mcp_server.py. Sin agent_host.py.
"""
import bpy
import json
import os
import re
import time
import threading
import traceback
import urllib.request
import logging
from datetime import datetime
from . import _axsock as bsock

logger = logging.getLogger("blender-mcp-auto")

_processed_ids = set()
_in_flight = {}
_message_start = {}
_timer_registered = False
_session_prefs = {}
_RETRY_LIMIT = 1


def start():
    global _timer_registered
    if _timer_registered:
        return
    bpy.app.timers.register(_tick, first_interval=0.5)
    _timer_registered = True


def _tick():
    try:
        with bsock._chat_lock:
            if not bsock._chat_queue:
                return _check_in_flight()
            messages = list(bsock._chat_queue)

        for msg in messages:
            mid = msg["id"]
            if mid in _processed_ids or mid in _in_flight:
                continue
            _in_flight[mid] = time.time()

            if mid not in _message_start:
                _message_start[mid] = time.time()

            elapsed = time.time() - _message_start[mid]
            text = msg["message"]
            print(f"[AUTO] mid={mid[:8]} text={text[:40]} elapsed={elapsed:.1f}s")

            if _try_auto_start_client():
                _process_with_client(mid, text)
                continue

            if elapsed > 30:
                del _in_flight[mid]
                txt = _diagnose()
                _respond(mid, txt)
                _cleanup(mid)

        return _check_in_flight()

    except Exception as e:
        logger.error(f"auto_process error: {e}")
        return 0.5


def _check_in_flight():
    now = time.time()
    for mid, started in list(_in_flight.items()):
        elapsed = now - started
        if elapsed > 30:
            _respond(mid, f"⏳ Generando... (ya van {elapsed:.0f}s)", is_status=True)
            return 2.0
    return 0.5


def _detect_provider(model_id):
    PROVIDER_ORDER = ["google", "anthropic", "deepseek", "opencode-go", "openrouter"]
    _PROVIDER_API = {
        "deepseek": {"url": "https://api.deepseek.com/v1/models", "auth": True},
        "opencode-go": {"url": "https://opencode.ai/zen/go/v1/models", "auth": True},
        "openrouter": {"url": "https://openrouter.ai/api/v1/models", "auth": False},
        "google": {"url": "https://generativelanguage.googleapis.com/v1beta/models", "auth": True},
        "anthropic": {"url": "https://api.anthropic.com/v1/models", "auth": True},
    }
    for pid in PROVIDER_ORDER:
        if model_id.startswith(pid):
            return pid
    for pid in _PROVIDER_API:
        if pid in model_id:
            return pid
    return "opencode-go"


def _get_api_key(provider):
    env_map = {"opencode-go": "OPENAI_API_KEY", "deepseek": "DEEPSEEK_API_KEY",
               "openrouter": "OPENROUTER_API_KEY", "anthropic": "ANTHROPIC_API_KEY",
               "google": "GOOGLE_API_KEY"}
    key = os.environ.get(env_map.get(provider, ""), "")
    if key:
        return key
    try:
        from .platform_utils import get_opencode_auth_path
        p = get_opencode_auth_path()
        if p.exists():
            auth = json.loads(p.read_text())
            entry = auth.get(provider, {})
            if isinstance(entry, dict) and entry.get("key"):
                return entry["key"]
    except:
        pass
    try:
        from .config_cache import get_provider_config
        return get_provider_config(provider).get("api_key", "")
    except:
        pass
    return ""


_CHAT_URLS = {
    "opencode-go": "https://opencode.ai/zen/go/v1/chat/completions",
    "openai": "https://api.openai.com/v1/chat/completions",
    "deepseek": "https://api.deepseek.com/v1/chat/completions",
    "openrouter": "https://openrouter.ai/api/v1/chat/completions",
    "google": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
    "anthropic": "https://api.anthropic.com/v1/messages",
    "ollama": "http://localhost:11434/v1/chat/completions",
}

_ANTHROPIC_HEADERS = {
    "anthropic-version": "2023-06-01",
    "content-type": "application/json",
}

SYSTEM_PROMPT = """Eres un asistente integrado en Blender 3D (Blender 4.2, Python API). Genera código Python completo.

INTERACCIÓN:
- Responde NATURALMENTE en el mismo idioma del usuario.
- Si el usuario pide algo vago, haz MÁXIMO 1 pregunta y LUEGO CREA con defaults.
- Después de crear, sugiere 1 mejora breve.
- Si preguntan "mejora esto", refiérete al último objeto creado.

# EJECUCIÓN DE CÓDIGO

`execute_blender_code` es last resort. Si hay otras tools para lo que necesitas, úsalas primero.

Prefiere operators (`bpy.ops`) para acciones estándar. Usa data API (`bpy.data`) para control preciso.

Muchos operators dependen del modo actual (Object, Edit, Sculpt...). Verifica o establece el modo primero.
El **active object** y **selection** son distintos. Muchos operators requieren ambos.
Establécelos explícitamente. Los operators cambian selection/active como efecto secundario,
reestablácelos entre llamadas secuenciales.

Actualiza el dependency graph después de cambios antes de leer propiedades computadas
(matrices world, resultados de modifiers, etc.).

En edit mode, accede a geometry via bmesh API, no mesh data API directa.
Flush bmesh changes al mesh.

Devuelve datos estructurados (dicts, lists) del código ejecutado.

# ESTRUCTURA DE ESCENA Y DATOS

Blender usa datablocks: objetos y sus datos (mallas, materiales, cámaras) son entidades separadas.

Jerarquía:
  * **Scene** — contenedor top-level. Un .blend puede tener múltiples.
  * **View Layer** — controla visibilidad/selectabilidad de colecciones.
  * **Collection** — árbol organizacional. Los objetos viven en colecciones; pueden anidarse;
    los objetos pueden pertenecer a múltiples colecciones.
  * **Object** — tiene transform (location, rotation, scale) y referencia datos subyacentes
    (Mesh, Curve, Camera...). Múltiples objetos pueden compartir el mismo dato (linked duplicates).
  * **Datablock** — los datos reales: geometría, materiales, texturas, etc.

Conceptos clave:
  * Objetos y datos están separados — eliminar uno no elimina el otro.
  * Datablocks huérfanos (zero users) se purgan al guardar/recargar.
  * Objetos creados via data API deben linkearse a una colección para aparecer en escena.
  * Datos compartidos: revisa user count antes de modificar un datablock.
    Haz single-user primero si es necesario.

Visibilidad tiene 3 estados independientes:
  * **Viewport hidden** — aún totalmente scripteable.
  * **Disabled in view layer** — excluido; inaccesible para operators dependientes de view layer.
  * **Disabled for render** — se salta en render, por lo demás normal.
  Revisa estos cuando objetos parezcan "perdidos" o los operators los salten.

Blender defaults a metros. Revisa scene unit settings antes de crear objetos dimensionados.

Explorar escenas:
  * Camina la jerarquía de colecciones primero.
  * No dumpees escenas enteras — inspecciona progresivamente.
  * Revisa object types, parenting, modifiers, materials antes de hacer cambios.

# TIPOS DE OBJETO Y CREACIÓN

Tipos: Mesh, Curve, Surface, Metaball, Text, Armature, Lattice,
Empty, Camera, Light, Light Probe, Grease Pencil.

Creación:
  * Operators para primitivas estándar — manejan defaults y colecciones.
  * Data API para creación procedural/batch — evita side effects.
  * Siempre linkea nuevos objetos a una colección.
  * Los nombres auto-agregan .001, .002 al colisionar — captura referencias inmediatamente
    después de crear, NUNCA busques por nombre asumido.

Elimina con unlinking habilitado para limpiar de todas las colecciones.

Prefiere workflows no-destructivos: modifiers sobre ediciones directas de mesh.

# TRANSFORMACIONES Y ESPACIOS DE COORDENADAS

Location, rotation, scale están en espacio local (relativo al padre, o world si no tiene padre).

Rotation mode determina qué propiedad usar (Euler, Quaternion, Axis-Angle).
Siempre revisa rotation mode primero — escribir en la propiedad incorrecta se ignora silenciosamente.

Espacios de coordenadas:
  * **World** — global. Usa world matrix para posiciones confiables.
  * **Local** — relativo al padre. Location/rotation/scale operan aquí.
  * **Object** — el sistema propio del objeto. Los vértices están en object space;
    multiplica por world matrix para world positions.

Estrategias:
  * El origin es el punto de referencia para location; los vértices son relativos a él.
  * Aplica transforms (especialmente scale) antes de operaciones dependientes de geometría
    (booleans, physics) — escala no-uniforme causa resultados inesperados.
  * Usa world matrix para lecturas en world space, no composición manual de
    location/rotation/scale.

# ORGANIZACIÓN DE ESCENA

- REVISA la escena actual (se te da como contexto) para nombres y posiciones existentes.
- NUNCA borres objetos existentes. Solo crea nuevos.
- NUNCA apiles en (0,0,0). Usa la posición sugerida en el contexto.
- Nombres ÚNICOS: si "Dona" ya existe, usa "Dona_001", "Dona_002", etc.
- "hola" → bpy.ops.object.text_add(location=(0, 2, 0)). body = "Hola".
- Multi-partes: 1) col = bpy.data.collections.new("Nombre")
  2) bpy.context.collection.children.link(col)
  3) col.objects.link(parte) para cada parte.
  ⚠️ NO uses NUNCA unlink() — causa error "not in collection".

# ESTÁNDAR DE DETALLE MÍNIMO
- Vehículo: carrocería + parabrisas + faros + ruedas con llanta.
- Mueble: todas las partes visibles con proporciones reales.
- Fruta/orgánico: forma reconocible + tallo + color.
- Edificio: paredes + techo + puerta + ventanas.
- SIEMPRE usa materiales con color. NO dejes nada sin material.

# HELPERS DISPONIBLES
- `make_lathe(profile, name, loc)` — revolución. Sirve para: tazas, botellas, floreros.
- `make_curve(points, bevel)` — curva Bezier con grosor.
- `make_collection(name)` — crea colección.
- NO uses primitivas para objetos curvos. Usa helpers.

# PREFERENCIAS DEL USUARIO
- Si el usuario dice "me gusta el rojo" o similar, lo recordaré.

# REGLAS ESTRICTAS DE CÓDIGO
- Cada instrucción en UNA sola línea.
- Usa `bpy.context.active_object`. NUNCA `bpy.context.object`.
- Modifier: `obj.modifiers.new(name="...", type='...')`. NO `bpy.ops.object.modifier_add`.
- Materiales: Principled BSDF con RGBA. Sin Specular.
- ESCALAS: `primitive_cube_add(size=1)` → cubo de 1m. scale ES el tamaño final. NO /2.
- Termina con `print("OK")`.
- Código en ```python ... ```.

APIS SEGURAS (NO alucines nombres de funciones):
- Para cilindros: bpy.ops.mesh.primitive_cylinder_add(radius=..., depth=..., location=..., rotation=...)
- Para cubos: bpy.ops.mesh.primitive_cube_add(size=1, location=...)
- Para esferas: bpy.ops.mesh.primitive_uv_sphere_add(radius=..., location=...)
- Para planos: bpy.ops.mesh.primitive_plane_add(size=..., location=...)
- NO uses bmesh.ops.create_cone, create_cylinder ni create_cube
- NO uses bmesh.ops con nombres que no conoces
- NO alucines nombres de funciones. Usa solo bpy.ops.mesh.primitive_* que conoces.

Ejemplo:
```python
import bpy
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 0))
s = bpy.context.active_object
s.name = "MiEsfera"
mod = s.modifiers.new(name="Subdiv", type='SUBSURF')
mod.levels = 2
mat = bpy.data.materials.new(name="Mat")
mat.use_nodes = True
mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (1, 0, 0, 1)
s.data.materials.append(mat)
print("OK")
```"""


# ─── Helpers para código generado ───

def _make_bezier_curve(name, points, bevel_depth=0.05, location=(0, 0, 0)):
    curve_data = bpy.data.curves.new(name=name + "Data", type='CURVE')
    curve_data.dimensions = '2D'
    curve_data.resolution_u = 12
    curve_data.bevel_depth = bevel_depth
    spline = curve_data.splines.new('BEZIER')
    spline.bezier_points.add(len(points) - 1)
    for i, co in enumerate(points):
        spline.bezier_points[i].co = co
    obj = bpy.data.objects.new(name, curve_data)
    obj.location = location
    bpy.context.collection.objects.link(obj)
    return obj


def _make_collection(name):
    col = bpy.data.collections.new(name)
    bpy.context.collection.children.link(col)
    return col


def _make_lathe(profile, name="LatheObj", location=(0, 0, 0), axis="Y", steps=64):
    if axis == "Y":
        pts = [(x, y, 0) for x, y in profile]
    else:
        pts = [(0, x, y) for x, y in profile]
    curve_data = bpy.data.curves.new(name=name + "Curve", type='CURVE')
    curve_data.dimensions = '2D'
    curve_data.resolution_u = steps
    spline = curve_data.splines.new('POLY')
    spline.points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        spline.points[i].co = (p[0], p[1], p[2], 1)
    obj = bpy.data.objects.new(name, curve_data)
    obj.location = location
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.ops.object.convert(target='MESH')
    bpy.ops.object.modifier_add(type='SCREW')
    mod = obj.modifiers[-1]
    if axis == "Y":
        mod.axis = 'Y'
    else:
        mod.axis = 'X'
    mod.steps = steps // 2
    mod.render_steps = steps // 2
    mod.use_merge_vertices = True
    bpy.ops.object.modifier_apply(modifier=mod.name)
    return obj


def _ensure_unique_name(base):
    if base not in bpy.data.objects:
        return base
    i = 1
    while f"{base}_{i:03d}" in bpy.data.objects:
        i += 1
    return f"{base}_{i:03d}"


def _get_next_position():
    occupied = [obj.location.x for obj in bpy.context.scene.objects]
    if not occupied:
        return 0.0
    return max(occupied) + 3.0


def _render_preview():
    fp = "/tmp/blender_mcp_preview.png"
    bpy.context.scene.render.filepath = fp
    bpy.context.scene.render.resolution_x = 800
    bpy.context.scene.render.resolution_y = 600
    bpy.ops.render.render(write_still=True)
    import base64
    with open(fp, "rb") as f:
        return base64.b64encode(f.read()).decode()


_HELPER_NAMESPACE = {
    "bpy": bpy, "C": bpy.context, "D": bpy.data, "ops": bpy.ops,
    "make_curve": _make_bezier_curve,
    "make_collection": _make_collection,
    "make_lathe": _make_lathe,
    "render_preview": _render_preview,
    "unique_name": _ensure_unique_name,
    "next_pos": _get_next_position,
}


# ─── Sesión: preferencias del usuario ───

def _parse_preferences(text, content):
    global _session_prefs
    text_lower = (text + " " + content).lower()
    color_keywords = {
        "rojo": (1, 0, 0, 1), "red": (1, 0, 0, 1),
        "azul": (0, 0, 1, 1), "blue": (0, 0, 1, 1),
        "verde": (0, 1, 0, 1), "green": (0, 1, 0, 1),
        "negro": (0, 0, 0, 1), "black": (0, 0, 0, 1),
        "blanco": (1, 1, 1, 1), "white": (1, 1, 1, 1),
        "amarillo": (1, 1, 0, 1), "yellow": (1, 1, 0, 1),
        "naranja": (1, 0.6, 0, 1), "orange": (1, 0.6, 0, 1),
        "morado": (0.5, 0, 1, 1), "purple": (0.5, 0, 1, 1),
        "rosa": (1, 0.4, 0.7, 1), "pink": (1, 0.4, 0.7, 1),
        "marrón": (0.5, 0.25, 0.1, 1), "brown": (0.5, 0.25, 0.1, 1),
        "gris": (0.5, 0.5, 0.5, 1), "gray": (0.5, 0.5, 0.5, 1),
    }
    for word, rgba in color_keywords.items():
        if word in text_lower and ("me gusta" in text_lower or "prefiero" in text_lower or "color" in text_lower):
            _session_prefs["color"] = rgba
            _session_prefs["color_name"] = word
            break


def _get_prefs_context():
    if not _session_prefs:
        return ""
    parts = []
    if "color_name" in _session_prefs:
        parts.append(f"color favorito: {_session_prefs['color_name']}")
    if "estilo" in _session_prefs:
        parts.append(f"estilo: {_session_prefs['estilo']}")
    return "Preferencias del usuario: " + ", ".join(parts) + "."


# ─── Ejecución de código en main thread ───

def _strip_bad_code(code):
    import re
    code = re.sub(r'^[ \t]*bpy\.context\.collection\.objects\.unlink\([^)]+\)\s*\n', '', code, flags=re.MULTILINE)
    code = re.sub(r'^[ \t]*bpy\.context\.scene\.collection\.objects\.unlink\([^)]+\)\s*\n', '', code, flags=re.MULTILINE)
    def _fix_scale(m):
        inner = m.group(1)
        inner = re.sub(r'\s*/\s*2\s*', '', inner)
        return '.scale = (' + inner + ')'
    code = re.sub(r'\.scale\s*=\s*\(([^)]*)\)', _fix_scale, code)
    return code

def _validate_code(code):
    try:
        from ..src.blender_mcp.utils.validator import validate
    except ImportError:
        try:
            from blender_mcp.utils.validator import validate
        except ImportError:
            return []
    return validate(code)

def _exec_code_main(code_blocks):
    results = []
    done = threading.Event()

    def execute():
        from .weak_sandbox import WeakSandboxForLLM
        for code in code_blocks:
            code = _strip_bad_code(code)
            errors = _validate_code(code)
            if errors:
                for e in errors:
                    results.append(str(e))
                continue
            try:
                import io
                from contextlib import redirect_stdout
                bpy.ops.ed.undo_push(message="AI ACTION")
                compiled = compile(code, "<blender_code>", "exec")
                buf = io.StringIO()
                with WeakSandboxForLLM():
                    with redirect_stdout(buf):
                        exec(compiled, _HELPER_NAMESPACE)
                bpy.context.view_layer.update()
                output = buf.getvalue().strip()
                if output:
                    results.insert(0, "__STDOUT__:" + output)
                print("[AUTO] Código ejecutado correctamente")
            except Exception as e:
                err = f"Error: {e}"
                print(f"[AUTO] {err}")
                results.append(err)
        if not results:
            try:
                b64 = _render_preview()
                results.insert(0, "__PREVIEW__:" + b64)
            except:
                pass
        done.set()
        return None

    bpy.app.timers.register(execute, first_interval=0.0)
    done.wait(timeout=10)
    return results


def _append_to_log(text, tag="AI"):
    try:
        log_path = os.path.expanduser("~/.config/blender-mcp/chat_log.txt")
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, "a") as f:
            f.write(f"[{datetime.now().strftime('%H:%M')}] {tag}: {text}\n\n")
    except:
        pass


def _get_scene_context():
    lines = []
    names = []
    for obj in bpy.context.scene.objects:
        loc = obj.location
        dims = obj.dimensions
        lines.append(f"- {obj.name} | {obj.type} | ({loc.x:.2f}, {loc.y:.2f}, {loc.z:.2f}) | ({dims.x:.2f}, {dims.y:.2f}, {dims.z:.2f})")
        names.append(obj.name)
    ctx = "Estado actual de la escena:\n" + "\n".join(lines) if lines else "Escena vacía."
    ctx += f"\nNombres ocupados: {', '.join(names) if names else '(ninguno)'}"
    ctx += f"\nSiguiente posición X libre: {_get_next_position():.1f}"
    return ctx


def _get_timeout(text):
    if len(text) > 50 or any(w in text.lower() for w in ("detalle", "detallado", "completo", "complej", "carro", "vehículo", "edificio", "mueble", "organico", "escena")):
        return 90
    return 60

def _call_llm(url, headers, model, messages, text=""):
    body = json.dumps({
        "model": model,
        "messages": messages,
        "max_tokens": 8192,
        "temperature": 0.4,
    }).encode()
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=_get_timeout(text)) as resp:
        return json.loads(resp.read())


def _call_anthropic(url, headers, api_key, model, messages, text=""):
    system = ""
    msgs = []
    for m in messages:
        if m["role"] == "system":
            system += m["content"] + "\n"
        elif m["role"] in ("user", "assistant"):
            msgs.append({"role": m["role"], "content": m["content"]})
    body = json.dumps({
        "model": model,
        "max_tokens": 8192,
        "system": system.strip(),
        "messages": msgs,
        "temperature": 0.4,
    }).encode()
    hdrs = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    req = urllib.request.Request(url, data=body, headers=hdrs, method="POST")
    with urllib.request.urlopen(req, timeout=_get_timeout(text)) as resp:
        return json.loads(resp.read())


_VISION_PROVIDERS = {"opencode-go", "openai", "openrouter", "google", "anthropic"}

def _capture_screenshot_b64():
    try:
        from .handlers.analysis import AnalysisHandler
        return AnalysisHandler.cmd_get_screenshot_as_base64()
    except:
        return None


def _process_with_client(mid, text):
    scene = bpy.context.scene
    model = getattr(scene, "aimcp_model", "")
    provider = _detect_provider(model) if model else "opencode-go"
    print(f"[AUTO] provider={provider} model={model}")
    api_key = _get_api_key(provider)
    print(f"[AUTO] api_key={'✅' if api_key else '❌'}")

    if not api_key:
        _respond(mid, "❌ No hay API key para " + provider)
        _cleanup(mid)
        return

    url = _CHAT_URLS.get(provider)
    if not url:
        _respond(mid, f"❌ Provider {provider} no soportado")
        _cleanup(mid)
        return

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "User-Agent": "blender-mcp/0.8",
    }

    timeout = _get_timeout(text)
    if timeout > 60:
        _respond(mid, "⏳ Generando código detallado...", is_status=True)
    else:
        _respond(mid, "⏳ Pensando...", is_status=True)

    def process():
        nonlocal text
        is_timeout_retry = False

        for retry in range(_RETRY_LIMIT + 1):
            if bsock._stop_agent:
                _respond(mid, "⛔ Detenido por el usuario")
                _cleanup(mid)
                return
            if retry > 0:
                if is_timeout_retry:
                    print(f"[AUTO] Reintento por timeout, prompt simplificado...")
                    text = f"{text_original}. Genera código CORTO, solo las partes más importantes, máximo 30 líneas."
                else:
                    print(f"[AUTO] Reintento {retry}/{_RETRY_LIMIT} con feedback de error...")
                    ctx = _get_scene_context()
                    text = text_original

            messages = [{"role": "system", "content": SYSTEM_PROMPT}]

            ctx = _get_scene_context()
            messages.append({"role": "system", "content": ctx})
            if retry > 0 and not is_timeout_retry:
                messages.append({"role": "system", "content": f"El intento anterior falló. Error: {errors[0]}. Escena actualizada arriba. Corrige el código."})

            prefs = _get_prefs_context()
            if prefs:
                messages.append({"role": "system", "content": prefs})

            user_msg = text

            if provider in _VISION_PROVIDERS:
                shot = _capture_screenshot_b64()
                if shot and "base64" in shot:
                    user_msg = [
                        {"type": "text", "text": text},
                        {"type": "image_url", "image_url": {"url": f"data:{shot['mime']};base64,{shot['base64']}"}},
                    ]

            messages.append({"role": "user", "content": user_msg})

            is_anthropic = provider == "anthropic"
            try:
                if is_anthropic:
                    result = _call_anthropic(url, headers, api_key, model, messages, text)
                    content = ""
                    for block in result.get("content", []):
                        if block.get("type") == "text":
                            content += block.get("text", "")
                else:
                    result = _call_llm(url, headers, model, messages, text)
                    content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            except urllib.error.HTTPError as e:
                err = e.read().decode()[:200]
                print(f"[AUTO] HTTP Error {e.code}: {err}")
                if retry < _RETRY_LIMIT:
                    text_original = text
                    text = f"Error HTTP {e.code}. Reintenta con código más simple."
                    continue
                _respond(mid, f"❌ HTTP {e.code}")
                _cleanup(mid)
                return
            except Exception as e:
                is_timeout = isinstance(e, TimeoutError) or "timed out" in str(e).lower()
                if is_timeout and retry < _RETRY_LIMIT:
                    text_original = text
                    is_timeout_retry = True
                    _respond(mid, "⏳ Simplificando y reintentando...", is_status=True)
                    continue
                print(f"[AUTO] Error: {traceback.format_exc()}")
                _respond(mid, f"❌ Error: {str(e)[:60]}")
                _cleanup(mid)
                return

            if not content:
                _respond(mid, "⚠️ El modelo no generó respuesta")
                _cleanup(mid)
                return

            print(f"[AUTO] Respuesta recibida ({len(content)} chars)")

            _parse_preferences(text, content)

            code_blocks = re.findall(r'```python\n(.*?)```', content, re.DOTALL)
            errors = []
            if code_blocks:
                print(f"[AUTO] Ejecutando {len(code_blocks)} bloque(s) de código en main thread...")
                errors = _exec_code_main(code_blocks)

            if not errors:
                break

            if retry == 0:
                text_original = text

        preview_b64 = None
        for e in errors:
            if e.startswith("__PREVIEW__:"):
                preview_b64 = e[12:]
                errors.remove(e)
                break
        if errors:
            content += "\n\n---\n⚠️ Error al ejecutar:\n" + "\n".join(errors)
        if preview_b64:
            content += "\n\n![preview](data:image/png;base64," + preview_b64 + ")"

        _respond(mid, content)
        _cleanup(mid)

    threading.Thread(target=process, daemon=True).start()


def _try_auto_start_client():
    scene = bpy.context.scene
    provider = getattr(scene, "aimcp_provider", "opencode-go")
    api_key = _get_api_key(provider)
    has_key = bool(api_key)
    print(f"[AUTO] _try_auto_start: provider={provider} key={'✅' if has_key else '❌'}")
    return has_key


def _respond(mid, text, is_status=False):
    def update():
        for s in bpy.data.scenes:
            for i, m in enumerate(s.aimcp_chat.msgs):
                if m.role == "status" and m.text.endswith("..."):
                    s.aimcp_chat.msgs.remove(i)
                    break
            if is_status:
                s.aimcp_chat.add("status", text, scene=s)
            else:
                s.aimcp_chat.add("assistant", text, scene=s)
                with bsock._chat_lock:
                    bsock._chat_queue[:] = [m for m in bsock._chat_queue if m["id"] != mid]
                s.aimcp_waiting = False
            s.aimcp_pending_msg_id = ""
            for screen in bpy.data.screens:
                for area in screen.areas:
                    area.tag_redraw()
            if not is_status:
                _append_to_log(text)
        return None
    bpy.app.timers.register(update, first_interval=0.0)


def _diagnose():
    lines = ["❌ No hay respuesta del agente. Diagnóstico:"]
    scene = bpy.context.scene

    provider = getattr(scene, "aimcp_provider", "?")
    model = getattr(scene, "aimcp_model", "?")
    api_key = _get_api_key(provider)

    if model and model != "?":
        lines.append(f"📌 Modelo: {model}")
    else:
        lines.append("📌 Ningún modelo seleccionado → Config → Refresh → selecciona uno")

    if api_key:
        lines.append(f"✅ API key presente para {provider}")
    else:
        lines.append(f"🔴 Falta API key para {provider}")
        lines.append("   • Ponla en variables de entorno")
        lines.append("   • O usa Local AI en Integrations (Ollama)")
        lines.append("   • O conecta Claude Desktop/Cursor como proxy")

    try:
        from .operators.embedded import _embedded_client
        if _embedded_client:
            lines.append("✅ Local AI activo")
        else:
            lines.append("ℹ️  Local AI no iniciado → click botón SYSTEM en el panel")
    except:
        pass

    try:
        import urllib.request
        req = urllib.request.Request("http://localhost:11434/api/version")
        with urllib.request.urlopen(req, timeout=2):
            lines.append("✅ Ollama detectado (pero no activo) → Integrations → Local AI")
    except:
        pass

    return "\n".join(lines)


def _cleanup(mid):
    _in_flight.pop(mid, None)
    _processed_ids.add(mid)
    _message_start.pop(mid, None)
