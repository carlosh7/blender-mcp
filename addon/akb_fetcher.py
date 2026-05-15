"""
blender-mcp — AKB Auto-Feeder
Busca objetos en Sketchfarm, extrae dimensiones, y guarda como Blueprint JSON v0.4.0.
Organizado por categorías: av, furniture, vehicles, structural, etc.
"""
import json
import os
from pathlib import Path

# ─── Configuración ───
AKB_DIR = Path(__file__).parent / "data" / "akb"

# Categorías a poblar con sus queries de búsqueda
DEFAULT_CATEGORIES = {
    "av": [
        "truss", "led wall", "moving head", "line array",
        "speaker", "subwoofer", "lighting fixture", "followspot",
        "stage deck", "riser", "curtain track", "hoist",
    ],
    "furniture": [
        "table", "chair", "desk", "shelf", "cabinet",
    ],
    "vehicles": [
        "car", "truck", "bus", "van",
    ],
    "structural": [
        "beam", "column", "scaffolding", "pipe",
    ],
}


def feed_from_sketchfab(category, keywords=None):
    """Busca modelos en Sketchfarm por keywords y guarda blueprints."""
    import bpy
    from addon.akb import save_blueprint, _calc_27_anchors

    if keywords is None:
        keywords = DEFAULT_CATEGORIES.get(category, [category])

    results = []
    for kw in keywords:
        print(f"[AKB Feeder] Buscando '{kw}' en Sketchfarm...")
        try:
            raw = bpy.ops.aimcp.search_sketchfab(query=kw)
        except:
            try:
                from .handlers.sketchfab import SketchfabHandler
                raw = SketchfabHandler.cmd_search_sketchfab(query=kw)
            except:
                print(f"[AKB] ❌ Error buscando '{kw}'")
                continue

        items = raw.get("results", raw) if isinstance(raw, dict) else raw
        if not items or not isinstance(items, list):
            items = [raw] if raw else []

        for item in items[:3]:  # Top 3 por keyword
            uid = item.get("uid", item.get("id", ""))
            name = item.get("name", kw).replace(" ", "_").lower()[:30]
            if not uid:
                continue

            try:
                detail = SketchfabHandler.cmd_get_sketchfab_preview(uid=uid)
            except:
                detail = {}

            dims = detail.get("dimensions", [1, 1, 1]) if isinstance(detail, dict) else [1, 1, 1]

            bp_data = {
                "name": item.get("name", kw),
                "source": "sketchfab",
                "source_id": uid,
                "mass_kg": detail.get("mass_kg", 0) if isinstance(detail, dict) else 0,
                "dimensions": dims,
                "functional_points": [],
            }

            fp = save_blueprint(bp_data, category, name)
            results.append({"name": name, "file": fp, "source": uid})
            print(f"[AKB] ✅ {name} guardado en {category}/")

    return {"category": category, "feeded": len(results), "items": results}


def feed_from_scanner(obj_name):
    """Escanea un objeto existente en Blender y lo guarda como blueprint."""
    import bpy
    from addon.akb import save_blueprint, _calc_27_anchors

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
    """Puebla todas las categorías por defecto desde Sketchfarm."""
    all_results = {}
    for category, keywords in DEFAULT_CATEGORIES.items():
        r = feed_from_sketchfab(category, keywords)
        all_results[category] = r
    return all_results
