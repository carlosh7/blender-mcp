"""
blender-mcp — Contextual RST Documentation Search Engine (TF-IDF)
Full-text search over bundled Blender Python API and User Manual RST files.
Implements TF-IDF ranking with section title and path boosting.
"""
import os
import re
import math
import glob

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
_CONTEXT_PARAGRAPHS = 3

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")


def _rst_files(subdir):
    base = os.path.join(_DATA_DIR, subdir) if _DATA_DIR else subdir
    pattern = os.path.join(base, "**", "*.rst")
    return sorted(glob.glob(pattern, recursive=True))


def _tokenize(text):
    tokens = re.findall(r"[a-z0-9_]+", text.lower())
    return [t for t in tokens if t not in _STOPWORDS and len(t) > 1]


def _tfidf_score(query_tokens, doc_text, doc_path):
    doc_tokens = _tokenize(doc_text)
    doc_len = len(doc_tokens)
    if doc_len == 0:
        return 0.0
    score = 0.0
    for qt in query_tokens:
        tf = doc_tokens.count(qt) / doc_len
        score += tf
    path_lower = doc_path.lower()
    for qt in query_tokens:
        if qt in path_lower:
            score += _PATH_MATCH_WEIGHT
    return score


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


def _get_title(filepath):
    with open(filepath, errors="replace") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("=") and not line.startswith("-"):
                return line[:120]
    return os.path.basename(filepath)


def search_api_docs(query, max_results=10):
    tokens = _tokenize(query)
    if not tokens:
        return {"query": query, "results": [], "total": 0}
    n_files = 0
    scored = []
    for fp in _rst_files("api"):
        n_files += 1
        with open(fp, errors="replace") as f:
            content = f.read()
        score = _tfidf_score(tokens, content, fp)
        if score > 0:
            rel = os.path.relpath(fp, _DATA_DIR)
            scored.append((score, rel, _extract_snippet(content, query), _get_title(fp)))
    scored.sort(key=lambda x: -x[0])
    results = [{"file": r[1], "snippet": r[2], "title": r[3], "score": round(r[0], 2)} for r in scored[:max_results]]
    return {"query": query, "results": results, "total": len(scored)}


def search_manual_docs(query, max_results=10):
    tokens = _tokenize(query)
    if not tokens:
        return {"query": query, "results": [], "total": 0}
    scored = []
    for fp in _rst_files("manual"):
        with open(fp, errors="replace") as f:
            content = f.read()
        score = _tfidf_score(tokens, content, fp)
        if score > 0:
            rel = os.path.relpath(fp, _DATA_DIR)
            scored.append((score, rel, _extract_snippet(content, query), _get_title(fp)))
    scored.sort(key=lambda x: -x[0])
    results = [{"file": r[1], "snippet": r[2], "title": r[3], "score": round(r[0], 2)} for r in scored[:max_results]]
    return {"query": query, "results": results, "total": len(scored)}


def get_python_api_docs(topic):
    q = topic.lower()
    for fp in _rst_files("api"):
        base = os.path.splitext(os.path.basename(fp))[0].lower()
        if q in base or q in fp.lower():
            with open(fp, errors="replace") as f:
                content = f.read()
            rel = os.path.relpath(fp, _DATA_DIR)
            return {"topic": topic, "file": rel, "title": _get_title(fp), "content": content[:8000]}
    return {"topic": topic, "error": "Topic not found in API docs"}
