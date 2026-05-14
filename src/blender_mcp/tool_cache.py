"""
blender-mcp — Tool Cache
Caches expensive tool results (get_scene_info, etc.) to avoid redundant Blender socket round-trips.
"""
import time

CACHE_TTL = 2.0  # seconds
_cache = {}


def get(cache_key):
    """Get cached value if not expired."""
    entry = _cache.get(cache_key)
    if entry and time.time() - entry["ts"] < CACHE_TTL:
        return entry["value"]
    return None


def set(cache_key, value):
    """Set cached value with current timestamp."""
    _cache[cache_key] = {"value": value, "ts": time.time()}


def invalidate(cache_key=None):
    """Invalidate cache. If key is None, clear all."""
    if cache_key:
        _cache.pop(cache_key, None)
    else:
        _cache.clear()
