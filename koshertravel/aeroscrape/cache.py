"""
High-Performance Route Cache for AeroScrape Flight Engine.
Automatically caches search results with a configurable Time-To-Live (TTL)
to return popular routes (e.g., NYC->TLV, LHR->TLV) in under 5 milliseconds.
"""
import time
import threading
from typing import Optional, Dict, Any, Tuple, List


class RouteCache:
    """
    Thread-safe TTL cache for flight query results.
    Default TTL is 15 minutes (900 seconds).
    """
    def __init__(self, ttl_seconds: int = 900):
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, Tuple[float, Any]] = {}
        self._lock = threading.Lock()
        self.hits = 0
        self.misses = 0

    def _make_key(self, origin: str, destination: str, date: str, return_date: Optional[str], cabin: str, pax: int, trip_type: str) -> str:
        return f"{origin.upper()}|{destination.upper()}|{date}|{return_date}|{cabin}|{pax}|{trip_type}"

    def get(self, origin: str, destination: str, date: str, return_date: Optional[str], cabin: str, pax: int, trip_type: str) -> Optional[Any]:
        key = self._make_key(origin, destination, date, return_date, cabin, pax, trip_type)
        with self._lock:
            if key in self._cache:
                timestamp, data = self._cache[key]
                if time.time() - timestamp < self.ttl_seconds:
                    self.hits += 1
                    return data
                else:
                    # Expired
                    del self._cache[key]
            self.misses += 1
            return None

    def set(self, origin: str, destination: str, date: str, return_date: Optional[str], cabin: str, pax: int, trip_type: str, data: Any):
        key = self._make_key(origin, destination, date, return_date, cabin, pax, trip_type)
        with self._lock:
            self._cache[key] = (time.time(), data)

    def clear(self):
        with self._lock:
            self._cache.clear()
            self.hits = 0
            self.misses = 0

    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            total = self.hits + self.misses
            hit_rate = round((self.hits / total) * 100.0, 1) if total > 0 else 0.0
            return {
                "cached_routes": len(self._cache),
                "cache_hits": self.hits,
                "cache_misses": self.misses,
                "hit_rate_pct": hit_rate,
                "ttl_seconds": self.ttl_seconds
            }


# Global shared cache instance for AeroScrape
GLOBAL_ROUTE_CACHE = RouteCache(ttl_seconds=900)
