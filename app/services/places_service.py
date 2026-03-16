from app.api.API_Places import (
    get_city_coordinates,
    get_tourist_attractions_nearby,
    get_place_id,
    get_place_id_from_coordinates,
    get_tourist_attraction
)
from app.models.attraction import AttractionCategory

from typing import Optional

class PlacesService:

    def get_city_coordinates(self, city_name: str) -> Optional[tuple]:
        return get_city_coordinates(city_name)

    def get_place_id(self, place_name: str, address: str = None) -> Optional[str]:
        return get_place_id(place_name, address)

    def get_place_id_from_coordinates(self, latitude: float, longitude: float) -> Optional[str]:
        return get_place_id_from_coordinates(latitude, longitude)

    async def get_tourist_attraction(self, place_id: str) -> Optional[dict]:
        return await get_tourist_attraction(place_id)

    def get_tourist_attractions_nearby(self, latitude: float, longitude: float, category) -> Optional[dict]:
        return get_tourist_attractions_nearby(latitude, longitude, category)