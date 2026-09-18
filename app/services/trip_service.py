from typing import Optional
from app.api.API_Trip import generate_city_trip, generate_road_trip
from app.services.ai_concurrency import user_concurrency_guard


class TripService:

    async def generate_city_trip(
        self,
        city_name: str,
        firstdate: str,
        lastdate: str,
        user_id: Optional[str] = None
    ):
        if user_id is None:
            return await generate_city_trip(city_name, firstdate, lastdate)
        async with user_concurrency_guard(user_id):
            return await generate_city_trip(city_name, firstdate, lastdate)

    async def generate_road_trip(
        self,
        region: str,
        firstdate: str,
        lastdate: str,
        user_id: Optional[str] = None
    ):
        if user_id is None:
            return await generate_road_trip(region, firstdate, lastdate)
        async with user_concurrency_guard(user_id):
            return await generate_road_trip(region, firstdate, lastdate)