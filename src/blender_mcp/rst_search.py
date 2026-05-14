"""
blender-mcp — RST Documentation Search Engine (lightweight)
Simple file-based search without docutils dependency.
Searches bundled Blender API and manual RST files.
"""
import os
import re
import glob

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")

def _rst_files(subdir=None):
    base = os.path.join(_DATA_DIR, subdir) if subdir else _DATA_DIR
    pattern = os.path.join(base, "**", "*.rst")
    return sorted(glob.glob(pattern, recursive=True))

def search_api_docs(query, max_results=10):
    q = query.lower()
    results = []
    for fp in _rst_files("api"):
        with open(fp, errors="replace") as f:
            content = f.read()
        if q in content.lower():
            rel = os.path.relpath(fp, _DATA_DIR)
            snippet = _extract_snippet(content, q)
            results.append({"file": rel, "snippet": snippet})
            if len(results) >= max_results:
                break
    return {"query": query, "results": results, "total": len(results)}

def search_manual_docs(query, max_results=10):
    q = query.lower()
    results = []
    for fp in _rst_files("manual"):
        with open(fp, errors="replace") as f:
            content = f.read()
        if q in content.lower():
            rel = os.path.relpath(fp, _DATA_DIR)
            snippet = _extract_snippet(content, q)
            results.append({"file": rel, "snippet": snippet})
            if len(results) >= max_results:
                break
    return {"query": query, "results": results, "total": len(results)}

def get_python_api_docs(topic):
    q = topic.lower()
    for fp in _rst_files("api"):
        base = os.path.splitext(os.path.basename(fp))[0].lower()
        if q in base or q in fp.lower():
            with open(fp, errors="replace") as f:
                content = f.read()
            rel = os.path.relpath(fp, _DATA_DIR)
            title = ""
            for line in content.split("\n")[:5]:
                if line.strip() and not line.startswith("#") and not line.startswith("="):
                    title = line.strip()[:100]
                    break
            return {"topic": topic, "file": rel, "title": title, "content": content[:5000]}
    return {"topic": topic, "error": "Topic not found in API docs"}

def _extract_snippet(text, query, width=120):
    idx = text.lower().find(query)
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
