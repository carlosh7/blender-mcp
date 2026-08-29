"""
blender-mcp-ultra — Cache Infrastructure
LRU cache and tool cache for performance optimization.
"""

import threading
import time
from collections import OrderedDict
from typing import Any, Optional


class LRUCache:
    """Thread-safe LRU cache with TTL support."""

    def __init__(self, maxsize: int = 128, default_ttl: int = 300):
        self.maxsize = maxsize
        self.default_ttl = default_ttl
        self._cache: OrderedDict = OrderedDict()
        self._ttl: dict = {}
        self._lock = threading.Lock()
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Any | None:
        with self._lock:
            if key in self._cache:
                # Check TTL
                if time.time() < self._ttl.get(key, float("inf")):
                    self._cache.move_to_end(key)
                    self._hits += 1
                    return self._cache[key]
                else:
                    # Expired
                    del self._cache[key]
                    self._ttl.pop(key, None)
            self._misses += 1
            return None

    def set(self, key: str, value: Any, ttl: int | None = None):
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
            self._cache[key] = value
            self._ttl[key] = time.time() + (ttl or self.default_ttl)
            if len(self._cache) > self.maxsize:
                oldest = next(iter(self._cache))
                del self._cache[oldest]
                self._ttl.pop(oldest, None)

    def delete(self, key: str) -> bool:
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._ttl.pop(key, None)
                return True
            return False

    def clear(self):
        with self._lock:
            self._cache.clear()
            self._ttl.clear()

    def has(self, key: str) -> bool:
        with self._lock:
            if key in self._cache:
                return time.time() < self._ttl.get(key, float("inf"))
            return False

    def size(self) -> int:
        with self._lock:
            return len(self._cache)

    def stats(self) -> dict:
        total = self._hits + self._misses
        return {
            "size": len(self._cache),
            "maxsize": self.maxsize,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": self._hits / total * 100 if total > 0 else 0,
        }


class ToolCache:
    """Cache specifically for tool execution results."""

    def __init__(self, maxsize: int = 256, default_ttl: int = 60):
        self._cache = LRUCache(maxsize=maxsize, default_ttl=default_ttl)

    def get_result(self, tool_name: str, params: dict) -> Any | None:
        key = self._make_key(tool_name, params)
        return self._cache.get(key)

    def set_result(self, tool_name: str, params: dict, result: Any, ttl: int = None):
        key = self._make_key(tool_name, params)
        self._cache.set(key, result, ttl)

    def invalidate(self, tool_name: str):
        """Invalidate all results for a tool."""
        with self._cache._lock:
            keys_to_delete = [k for k in self._cache._cache if k.startswith(f"{tool_name}:")]
            for key in keys_to_delete:
                del self._cache._cache[key]
                self._cache._ttl.pop(key, None)

    def clear(self):
        self._cache.clear()

    def stats(self) -> dict:
        return self._cache.stats()

    def _make_key(self, tool_name: str, params: dict) -> str:
        sorted_params = sorted(params.items())
        return f"{tool_name}:{sorted_params}"


# Singleton instances
_lru_cache = None
_tool_cache = None


def get_lru_cache(maxsize: int = 128, default_ttl: int = 300) -> LRUCache:
    global _lru_cache
    if _lru_cache is None:
        _lru_cache = LRUCache(maxsize=maxsize, default_ttl=default_ttl)
    return _lru_cache


def get_tool_cache(maxsize: int = 256, default_ttl: int = 60) -> ToolCache:
    global _tool_cache
    if _tool_cache is None:
        _tool_cache = ToolCache(maxsize=maxsize, default_ttl=default_ttl)
    return _tool_cache
