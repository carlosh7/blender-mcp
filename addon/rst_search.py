"""
blender-mcp — Contextual RST Documentation Search Engine (TF-IDF)
Full-text search over bundled Blender Python API and User Manual RST files.
Implements TF-IDF ranking with section title and path boosting.

Incluye timeout 2s con fallback a introspección de bpy.types.*
"""
import os
import re
import math
import glob
import threading
import logging

logger = logging.getLogger("blender-mcp-rst")

_STOPWORDS = frozenset({
    "a", "an", "the", "is", "it", "in", "on", "of", "to", "for", "and",
    "or", "but", "with", "as", "at", "by", "from", "so", "this", "that",
    "are", "was", "be", "been", "have", "has", "had", "do", "does", "did",
    "will", "would", "can", "could", "may", "might", "should", "about",
    "into", "over", "such", "only", "than", "then", "also", "very", "just",
    "how", "what", "when", "where", "which", "who", "why",
})

_TITLE_MATCH_WEIGHT = 15.0
_PATH_MATCH_WEIGHT = 10.0

_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def _rst_files(subdir):
    base = os.path.join(_DATA_DIR, subdir) if _DATA_DIR else subdir
    pattern = os.path.join(base, "**", "*.rst")
    return sorted(glob.glob(pattern, recursive=True))


def _tokenize(text):
    tokens = re.findall(r"[a-z0-9_]+", text.lower())
    return [t for t in tokens if t not in _STOPWORDS and len(t) > 1]


def _get_title(filepath):
    with open(filepath, errors="replace") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("=") and not line.startswith("-"):
                return line[:120]
    return os.path.basename(filepath)


def _extract_snippet(text, query, width=200):
    idx = text.lower().find(query.lower())
    if idx < 0:
        return text[:width]
    start = max(0, idx - width // 2)
    end = min(len(text), idx + width // 2)
    snippet = text[start:end]
    if start > 0:
        snippet = "..." + snippet
    if end < len(text):
        snippet = snippet + "..."
    return snippet


def _count_docs_containing(tokens, files):
    doc_counts = {}
    total_with_content = 0
    for fp in files:
        with open(fp, errors="replace") as f:
            content = f.read()
        if not content.strip():
            continue
        total_with_content += 1
        for qt in tokens:
            if qt in content.lower():
                doc_counts[qt] = doc_counts.get(qt, 0) + 1
    return doc_counts, total_with_content


def _score_doc(tokens, content, filepath, title, idf_weights):
    doc_tokens = _tokenize(content)
    doc_len = len(doc_tokens)
    if doc_len == 0:
        return 0.0
    score = 0.0
    for qt in tokens:
        tf = doc_tokens.count(qt) / doc_len
        idf = idf_weights.get(qt, 1.0)
        score += tf * idf
    path_lower = filepath.lower()
    for qt in tokens:
        if qt in path_lower:
            score += _PATH_MATCH_WEIGHT
    title_lower = title.lower()
    for qt in tokens:
        if qt in title_lower:
            score += _TITLE_MATCH_WEIGHT
    return score


def _search(subdir, query, max_results=10):
    tokens = _tokenize(query)
    if not tokens:
        return {"query": query, "results": [], "total": 0}
    files = _rst_files(subdir)
    if not files:
        return None
    doc_counts, total = _count_docs_containing(tokens, files)
    n = total or 1
    idf_weights = {qt: math.log((n + 1) / (doc_counts.get(qt, 0) + 1)) + 1 for qt in tokens}
    scored = []
    for fp in files:
        with open(fp, errors="replace") as f:
            content = f.read()
        if not content.strip():
            continue
        title = _get_title(fp)
        score = _score_doc(tokens, content, fp, title, idf_weights)
        if score > 0:
            rel = os.path.relpath(fp, _DATA_DIR)
            scored.append((score, rel, _extract_snippet(content, query), title))
    scored.sort(key=lambda x: -x[0])
    results = [{"file": r[1], "snippet": r[2], "title": r[3], "score": round(r[0], 2)} for r in scored[:max_results]]
    return {"query": query, "results": results, "total": len(scored), "source": "rst"}


def _search_with_timeout(subdir, query, max_results=10, timeout=2.0):
    result = [None]
    done = threading.Event()

    def worker():
        try:
            result[0] = _search(subdir, query, max_results)
        except Exception as e:
            logger.warning(f"RST search error: {e}")
        finally:
            done.set()

    t = threading.Thread(target=worker, daemon=True)
    t.start()
    if not done.wait(timeout=timeout):
        logger.warning(f"RST search timed out ({timeout}s) for: {query}")
        return None
    return result[0]


# ─── Fallback por introspección (0 MB, siempre disponible) ───

def _introspect_ops(query):
    import bpy
    tokens = _tokenize(query)
    if not tokens:
        return []
    results = []
    ops_categories = dir(bpy.ops)
    for cat_name in ops_categories:
        if cat_name.startswith("_"):
            continue
        cat = getattr(bpy.ops, cat_name, None)
        if not cat:
            continue
        for op_name in dir(cat):
            if op_name.startswith("_"):
                continue
            op = getattr(cat, op_name, None)
            if not op:
                continue
            doc = (op.__doc__ or "").strip()
            if not doc:
                continue
            full_name = f"bpy.ops.{cat_name}.{op_name}"
            score = 0
            for t in tokens:
                if t in full_name.lower():
                    score += _PATH_MATCH_WEIGHT
                if t in doc.lower():
                    score += 2.0
            if score > 0:
                snippet = _extract_snippet(doc, query, width=150)
                results.append({"file": full_name, "snippet": snippet, "title": full_name, "score": round(score, 2)})
    results.sort(key=lambda x: -x["score"])
    return results[:max_results]


def _introspect_topic(topic):
    import bpy
    parts = topic.replace("bpy.", "").split(".")
    obj = bpy
    chain = "bpy"
    for p in parts:
        if not p:
            continue
        try:
            obj = getattr(obj, p, None)
        except Exception:
            return {"topic": topic, "error": f"Cannot resolve: {chain}.{p}", "source": "introspect"}
        if obj is None:
            return {"topic": topic, "error": f"{chain}.{p} not found", "source": "introspect"}
        chain += f".{p}"
    doc = (obj.__doc__ or "").strip()[:4000]
    return {"topic": topic, "doc": doc, "source": "introspect"}


# ─── API pública ───

_SEARCH_CACHE = {}


def search_api_docs(query, max_results=10):
    if not query:
        return {"query": query, "results": [], "total": 0}
    cached = _SEARCH_CACHE.get(query)
    if cached:
        return cached
    result = _search_with_timeout("api", query, max_results)
    if result:
        _SEARCH_CACHE[query] = result
        return result
    intro = _introspect_ops(query)
    result = {"query": query, "results": intro, "total": len(intro), "source": "introspect"}
    _SEARCH_CACHE[query] = result
    return result


def get_python_api_docs(topic):
    if not topic:
        return {"topic": topic, "error": "No topic provided"}
    cached = _SEARCH_CACHE.get(f"doc:{topic}")
    if cached:
        return cached
    if not os.path.exists(os.path.join(_DATA_DIR, "api")):
        result = _introspect_topic(topic)
        _SEARCH_CACHE[f"doc:{topic}"] = result
        return result
    q = topic.lower().replace("bpy.", "", 1)
    for fp in _rst_files("api"):
        base = os.path.splitext(os.path.basename(fp))[0].lower()
        if q in base or q in fp.lower():
            with open(fp, errors="replace") as f:
                content = f.read()
            rel = os.path.relpath(fp, _DATA_DIR)
            result = {"topic": topic, "file": rel, "title": _get_title(fp), "content": content[:8000], "source": "rst"}
            _SEARCH_CACHE[f"doc:{topic}"] = result
            return result
    result = _introspect_topic(topic)
    _SEARCH_CACHE[f"doc:{topic}"] = result
    return result


def clear_cache():
    _SEARCH_CACHE.clear()
