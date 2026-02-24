from pydantic import BaseModel
from typing import List


class TripLocation(BaseModel):
    id: str
    locationName: str
    locationAdress: str
    countryCode: str
    latitude: float
    longitude: float
    date: str


class CityTripResponse(BaseModel):
    lieux: List[TripLocation]


class RoadTripResponse(BaseModel):
    villes: List[TripLocation]
    lieux: List[TripLocation]