from app.api.API_Places_AI import generate_attraction, generate_description
from typing import Optional
from app.core.logger import setup_logger
from app.services import ai_cache

logger = setup_logger(__name__)


class AIService:

    async def generate_attraction(
        self,
        place_name: str,
        address: Optional[str] = None,
        category: str = "autre"
    ):
        key = ai_cache.attraction_cache_key(place_name, address, category)
        if key in ai_cache.attraction_cache:
            logger.info(f"AI | Cache hit — attraction place={place_name}")
            return ai_cache.attraction_cache[key]
        result = await generate_attraction(place_name, address, category)
        if result:
            ai_cache.attraction_cache[key] = result
        return result

    async def generate_description(
        self,
        place_name: str,
        address: Optional[str] = None
    ) -> Optional[str]:
        key = ai_cache.description_cache_key(place_name, address)
        if key in ai_cache.description_cache:
            logger.info(f"AI | Cache hit — description place={place_name}")
            return ai_cache.description_cache[key]
        result = await generate_description(
            place_name=place_name,
            full_address=address
        )
        if result:
            ai_cache.description_cache[key] = result
        return result
