from app.api.API_Trip import generate_city_trip, generate_road_trip


class TripService:

    def generate_city_trip(
        self,
        city_name: str,
        firstdate: str,
        lastdate: str
    ):
        # generate_city_trip gère ses propres exceptions (dates invalides, etc.)
        return generate_city_trip(city_name, firstdate, lastdate)

    def generate_road_trip(
        self,
        region: str,
        firstdate: str,
        lastdate: str
    ):
        # generate_road_trip gère ses propres exceptions
        return generate_road_trip(region, firstdate, lastdate)