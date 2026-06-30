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

    async def get_city_coordinates(self, city_name: str) -> Optional[tuple]:
        return await get_city_coordinates(city_name)

    async def get_place_id(self, place_name: str, address: str = None) -> Optional[str]:
        return await get_place_id(place_name, address)

    async def get_place_id_from_coordinates(self, latitude: float, longitude: float) -> Optional[str]:
        return await get_place_id_from_coordinates(latitude, longitude)

    async def get_tourist_attraction(self, place_id: str, session_token: Optional[str] = None) -> Optional[dict]:
        return await get_tourist_attraction(place_id, session_token=session_token)

    async def get_tourist_attractions_nearby(self, latitude: float, longitude: float, category) -> Optional[dict]:
        return await get_tourist_attractions_nearby(latitude, longitude, category)