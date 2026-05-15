"""
blender-mcp — AKB Auto-Feeder
Busca objetos en Poly Haven (gratis, sin API key) y Sketchfarm,
extrae dimensiones reales, y guarda como Blueprint JSON v0.4.0.
"""
import json
import os
import sys
import tempfile
from pathlib import Path

AKB_DIR = Path(__file__).parent / "data" / "akb"

DEFAULT_CATEGORIES = {
    "av": ["truss", "speaker", "microphone", "camera", "monitor"],
    "furniture": ["table", "chair", "desk", "shelf", "cabinet", "bed"],
    "vehicles": ["car", "truck", "bus", "bicycle"],
    "structural": ["door", "window", "beam", "column"],
}


def _get_polyhaven_model_dimensions(asset_id):
    """Descarga un modelo de Poly Haven y extrae sus dimensiones reales."""
    import bpy
    import shutil
    import urllib.request
    sys.path.insert(0, str(Path(__file__).parent / "handlers"))
    from polyhaven import _api_get

    files_data = _api_get(f"files/{asset_id}")
    for fmt in ("gltf", "glb", "fbx", "obj"):
        for res in ("1k", "2k", "4k"):
            info = files_data.get(fmt, {}).get(res, {}).get(fmt)
            if info:
                break
        if info:
            break
    if not info:
        return None

    url = info["url"]
    tmp_dir = tempfile.mkdtemp()
    try:
        main_name = url.split("/")[-1]
        main_path = os.path.join(tmp_dir, main_name)
        req = urllib.request.Request(url, headers={"User-Agent": "blender-mcp/0.8"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            with open(main_path, "wb") as f:
                f.write(resp.read())

        inc = info.get("include", {})
        for rel_path, inc_info in inc.items():
            inc_url = inc_info["url"]
            inc_dest = os.path.join(tmp_dir, rel_path)
            os.makedirs(os.path.dirname(inc_dest), exist_ok=True)
            req = urllib.request.Request(inc_url, headers={"User-Agent": "blender-mcp/0.8"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                with open(inc_dest, "wb") as f:
                    f.write(resp.read())

        before = set(bpy.data.objects.keys())
        if fmt == "gltf":
            bpy.ops.import_scene.gltf(filepath=main_path)
        else:
            return None

        imported = [o for o in bpy.data.objects if o.name not in before]
        if not imported:
            return None

        dims = [0, 0, 0]
        for obj in imported:
            d = obj.dimensions
            dims[0] = max(dims[0], d.x)
            dims[1] = max(dims[1], d.y)
            dims[2] = max(dims[2], d.z)

        # Cleanup imported objects
        for obj in imported:
            bpy.data.objects.remove(obj, do_unlink=True)

        return [round(d, 4) for d in dims]
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def _search_polyhaven_models(query):
    """Busca modelos gratuitos en Poly Haven."""
    import urllib.request, json
    url = f"https://api.polyhaven.com/assets?type=models"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "blender-mcp/0.8"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
    except:
        return []

    results = []
    for aid, info in data.items():
        if query.lower() in aid.lower():
            results.append({
                "id": aid,
                "name": aid.replace("_", " ").title(),
                "type": info.get("type", "model"),
                "source": "polyhaven",
            })
    return results[:10]


def feed_from_polyhaven(category, keywords=None):
    """Busca modelos en Poly Haven (gratis), descarga, extrae dimensiones, guarda blueprint."""
    import bpy
    sys.path.insert(0, str(Path(__file__).parent))
    from akb import save_blueprint

    if keywords is None:
        keywords = DEFAULT_CATEGORIES.get(category, [category])

    results = []
    for kw in keywords:
        print(f"[AKB] Buscando '{kw}' en Poly Haven...")
        models = _search_polyhaven_models(kw)
        for model in models[:3]:
            aid = model["id"]
            print(f"[AKB]  Descargando {aid}...")
            dims = _get_polyhaven_model_dimensions(aid)
            if not dims:
                print(f"[AKB]  ❌ No se pudo obtener dimensiones de {aid}")
                continue

            bp_data = {
                "name": model["name"],
                "source": "polyhaven",
                "source_id": aid,
                "mass_kg": 0,
                "dimensions": dims,
                "functional_points": [],
            }
            name = aid.replace("-", "_").replace(".", "_")[:30]
            fp = save_blueprint(bp_data, category, name)
            results.append({"name": name, "file": fp, "dimensions": dims})
            print(f"[AKB]  ✅ {name}: {dims}")

    return {"category": category, "feeded": len(results), "items": results}


def feed_from_scanner(obj_name):
    """Escanea un objeto existente y lo guarda como blueprint."""
    import bpy
    sys.path.insert(0, str(Path(__file__).parent))
    from akb import save_blueprint

    obj = bpy.data.objects.get(obj_name)
    if not obj:
        return {"error": f"Object not found: {obj_name}"}

    dims = [round(d, 4) for d in obj.dimensions]
    bp_data = {
        "name": obj_name,
        "source": "scanner",
        "source_id": obj_name,
        "mass_kg": 0,
        "dimensions": dims,
        "functional_points": [],
    }
    fp = save_blueprint(bp_data, "scanned", obj_name)
    return {"name": obj_name, "file": fp, "dimensions": dims}


def feed_all():
    """Puebla todas las categorías desde Poly Haven."""
    all_results = {}
    for category, keywords in DEFAULT_CATEGORIES.items():
        r = feed_from_polyhaven(category, keywords)
        all_results[category] = r
    return all_results
