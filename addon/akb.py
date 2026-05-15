"""
blender-mcp — AKB (Axiom Knowledge Base) Manager
Almacena y consulta blueprints de objetos reales con schema v0.4.0.
Organizado por categorías: av/, furniture/, vehicles/, structural/, etc.
"""
import os
import json
import math
from pathlib import Path

_AKB_DIR = Path(__file__).parent / "data" / "akb"
_INDEX_FILE = _AKB_DIR / "_index.json"
_REPO_AKB = Path(os.path.expanduser("~")) / "blender-mcp" / "addon" / "data" / "akb"


def _ensure_dirs():
    _AKB_DIR.mkdir(parents=True, exist_ok=True)
    for cat in ["av", "furniture", "vehicles", "structural"]:
        (_AKB_DIR / cat).mkdir(exist_ok=True)


def _load_index():
    if _INDEX_FILE.exists():
        try:
            return json.loads(_INDEX_FILE.read_text())
        except:
            pass
    return []


def _save_index(index):
    _INDEX_FILE.write_text(json.dumps(index, indent=2))


def _calc_27_anchors(dims):
    """Calcula 27 puntos de ancla desde dimensiones [x, y, z]."""
    x, y, z = dims[0], dims[1], dims[2]
    hx, hy, hz = x / 2, y / 2, z / 2
    steps_x = [-hx, 0.0, hx]
    steps_y = [-hy, 0.0, hy]
    steps_z = [-hz, 0.0, hz]
    anchors = {}
    i = 0
    for sx in steps_x:
        for sy in steps_y:
            for sz in steps_z:
                anchors[f"V{i}"] = [round(sx, 4), round(sy, 4), round(sz, 4)]
                i += 1
    anchors["CENTROID"] = [0.0, 0.0, 0.0]
    anchors["C_FACE_TOP"] = [0.0, 0.0, round(hz, 4)]
    anchors["C_FACE_BOTTOM"] = [0.0, 0.0, round(-hz, 4)]
    return anchors


def save_blueprint(data, category, name):
    """Guarda un blueprint en disco con schema v0.4.0."""
    _ensure_dirs()
    cat_dir = _AKB_DIR / category
    cat_dir.mkdir(exist_ok=True)
    bp = {
        "metadata": {
            "category": f"{category}/{name}",
            "name": data.get("name", name),
            "source": data.get("source", "manual"),
            "source_id": data.get("source_id", ""),
            "mass_kg": data.get("mass_kg", 0),
            "ior_refraction": data.get("ior", 1.0),
            "electrical_watts": data.get("watts", 0),
            "material": data.get("material", ""),
        },
        "geometry": {
            "dimensions": data.get("dimensions", [1, 1, 1]),
            "anchors_27pt": _calc_27_anchors(data.get("dimensions", [1, 1, 1])),
            "topology_hash": data.get("topology_hash", None),
        },
        "functional_points": data.get("functional_points", []),
    }
    filepath = cat_dir / f"{name}.json"
    filepath.write_text(json.dumps(bp, indent=2))

    # Also save to repo for git tracking
    try:
        repo_cat = _REPO_AKB / category
        repo_cat.mkdir(parents=True, exist_ok=True)
        repo_fp = repo_cat / f"{name}.json"
        repo_fp.write_text(json.dumps(bp, indent=2))
        # Also update repo index
        repo_idx = _REPO_AKB / "_index.json"
        if repo_idx.exists():
            ridx = json.loads(repo_idx.read_text())
        else:
            ridx = []
        entry_r = {
            "name": name, "category": category,
            "display_name": data.get("name", name),
            "dimensions": data.get("dimensions", [1, 1, 1]),
            "source": data.get("source", "manual"),
        }
        if not any(e["name"] == name and e["category"] == category for e in ridx):
            ridx.append(entry_r)
        repo_idx.write_text(json.dumps(ridx, indent=2))
    except:
        pass

    index = _load_index()
    entry = {
        "name": name, "category": category,
        "display_name": data.get("name", name),
        "dimensions": data.get("dimensions", [1, 1, 1]),
        "source": data.get("source", "manual"),
    }
    existing = [e for e in index if e["name"] == name and e["category"] == category]
    if not existing:
        index.append(entry)
    _save_index(index)
    return str(filepath)


def _normalize(bp):
    """Asegura que el blueprint tenga schema v0.4.0 completo."""
    if "geometry" not in bp:
        dims = bp.get("dimensions", [1, 1, 1])
        bp["geometry"] = {
            "dimensions": dims,
            "anchors_27pt": _calc_27_anchors(dims),
            "topology_hash": bp.get("topology_hash", None),
        }
    if "metadata" not in bp:
        bp["metadata"] = {
            "category": bp.get("category", bp.get("name", "unknown")),
            "name": bp.get("name", "unknown"),
            "source": bp.get("source", "manual"),
            "source_id": bp.get("source_id", ""),
            "mass_kg": bp.get("mass_kg", 0),
            "ior_refraction": bp.get("ior", 1.0),
            "electrical_watts": bp.get("watts", 0),
            "material": bp.get("material", ""),
        }
    if "functional_points" not in bp:
        bp["functional_points"] = bp.get("functional_points", [])
    return bp


def get_specs(query):
    """Busca en AKB por nombre o categoría. Devuelve lista de blueprints normalizados (schema v0.4.0)."""
    q = query.lower().strip()
    _ensure_dirs()
    results = []
    index = _load_index()
    for entry in index:
        if q in entry["name"].lower() or q in entry["category"].lower() or q in entry["display_name"].lower():
            fp = _AKB_DIR / entry["category"] / f"{entry['name']}.json"
            if fp.exists():
                bp = json.loads(fp.read_text())
                results.append(_normalize(bp))
    return results


def list_categories():
    """Devuelve lista de categorías disponibles con conteo."""
    _ensure_dirs()
    index = _load_index()
    cats = {}
    for entry in index:
        cat = entry["category"]
        cats[cat] = cats.get(cat, 0) + 1
    return [{"category": k, "count": v} for k, v in sorted(cats.items())]


def get_blueprint_by_name(name):
    """Busca un blueprint específico por nombre exacto."""
    _ensure_dirs()
    index = _load_index()
    for entry in index:
        if entry["name"] == name:
            fp = _AKB_DIR / entry["category"] / f"{name}.json"
            if fp.exists():
                return json.loads(fp.read_text())
    return None
