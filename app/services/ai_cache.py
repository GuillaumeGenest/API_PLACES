from typing import Optional
from cachetools import TTLCache

_CACHE_TTL = 60 * 60 * 24  # 24h

description_cache: TTLCache = TTLCache(maxsize=500, ttl=_CACHE_TTL)
attraction_cache: TTLCache = TTLCache(maxsize=500, ttl=_CACHE_TTL)


def description_cache_key(place_name: str, address: Optional[str]) -> tuple:
    return (place_name.strip().lower(), (address or "").strip().lower())


def attraction_cache_key(place_name: str, address: Optional[str], category: str) -> tuple:
    return (place_name.strip().lower(), (address or "").strip().lower(), category.strip().lower())


def clear() -> None:
    """Empties both caches — used by tests to avoid state leaking between cases."""
    description_cache.clear()
    attraction_cache.clear()
