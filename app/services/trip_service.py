from app.api.API_Trip import generate_city_trip, generate_road_trip


class TripService:

    async def generate_city_trip(
        self,
        city_name: str,
        firstdate: str,
        lastdate: str
    ):
        return await generate_city_trip(city_name, firstdate, lastdate)

    async def generate_road_trip(
        self,
        region: str,
        firstdate: str,
        lastdate: str
    ):
        return await generate_road_trip(region, firstdate, lastdate)