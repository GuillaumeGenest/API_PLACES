from app.api.API_Places_AI import generate_attraction, generate_description
from typing import Optional


class AIService:

    def generate_attraction(
        self,
        place_name: str,
        address: Optional[str] = None,
        category: str = "autre"
    ):
        # generate_attraction gère ses propres exceptions en interne
        return generate_attraction(place_name, address, category)

    def generate_description(
        self,
        place_name: str,
        address: Optional[str] = None
    ) -> Optional[str]:
        # generate_description gère ses propres exceptions en interne
        return generate_description(
            place_name=place_name,
            full_address=address
        )