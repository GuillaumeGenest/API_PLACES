from app.api.API_Places_AI import generate_attraction, generate_description
from typing import Optional
from cachetools import TTLCache
from app.core.logger import setup_logger

logger = setup_logger(__name__)

# Cache en mémoire, au niveau module — AIService est instancié à chaque requête,
# donc un cache sur self serait recréé (et vidé) à chaque appel.
_CACHE_TTL = 60 * 60 * 24  # 24h
_description_cache: TTLCache = TTLCache(maxsize=500, ttl=_CACHE_TTL)
_attraction_cache: TTLCache = TTLCache(maxsize=500, ttl=_CACHE_TTL)


def _description_cache_key(place_name: str, address: Optional[str]) -> tuple:
    return (place_name.strip().lower(), (address or "").strip().lower())


def _attraction_cache_key(place_name: str, address: Optional[str], category: str) -> tuple:
    return (place_name.strip().lower(), (address or "").strip().lower(), category.strip().lower())


class AIService:

    async def generate_attraction(
        self,
        place_name: str,
        address: Optional[str] = None,
        category: str = "autre"
    ):
        key = _attraction_cache_key(place_name, address, category)
        if key in _attraction_cache:
            logger.info(f"AI | Cache hit — attraction place={place_name}")
            return _attraction_cache[key]
        result = await generate_attraction(place_name, address, category)
        if result:
            _attraction_cache[key] = result
        return result

    async def generate_description(
        self,
        place_name: str,
        address: Optional[str] = None
    ) -> Optional[str]:
        key = _description_cache_key(place_name, address)
        if key in _description_cache:
            logger.info(f"AI | Cache hit — description place={place_name}")
            return _description_cache[key]
        result = await generate_description(
            place_name=place_name,
            full_address=address
        )
        if result:
            _description_cache[key] = result
        return result