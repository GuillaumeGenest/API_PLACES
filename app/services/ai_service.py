from app.api.API_Places_AI import generate_attraction, generate_description
from typing import Optional

class AIService:

    async def generate_attraction(
        self,
        place_name: str,
        address: Optional[str] = None,
        category: str = "autre"
    ):
        return await generate_attraction(place_name, address, category)

    async def generate_description(
        self,
        place_name: str,
        address: Optional[str] = None
    ) -> Optional[str]:
        return await generate_description(
            place_name=place_name,
            full_address=address
        )