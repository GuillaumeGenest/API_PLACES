from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.services.places_service import PlacesService
from app.models.attraction import AttractionCategory
from app.core.exceptions import PlaceNotFoundError, AttractionNotFoundError

router = APIRouter(prefix="/attractions", tags=["Attractions"])

@router.get("/")
def get_attractions(city_name: str, category: AttractionCategory):
    service = PlacesService()
    coordinates = service.get_city_coordinates(city_name)
    if not coordinates:
        raise PlaceNotFoundError(city_name)

    attractions = service.get_tourist_attractions_nearby(
        coordinates[0], coordinates[1], category
    )
    if not attractions:
        raise AttractionNotFoundError()
    return JSONResponse(content=attractions)


@router.get("/by_coordinates")
def get_attractions_by_coordinates(
    latitude: float,
    longitude: float,
    category: AttractionCategory
):
    service = PlacesService()
    attractions = service.get_tourist_attractions_nearby(latitude, longitude, category)
    if not attractions:
        raise AttractionNotFoundError()
    return JSONResponse(content=attractions)