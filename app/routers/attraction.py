from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.services.places_service import PlacesService
from app.core.exceptions import PlaceNotFoundError, AttractionNotFoundError

router = APIRouter(prefix="/attraction", tags=["Attraction"])

@router.get("/by_name")
def get_attraction_by_name(place_name: str, address: str):
    service = PlacesService()
    place_id = service.get_place_id(place_name, address)
    if not place_id:
        raise PlaceNotFoundError(place_name)

    attraction = service.get_tourist_attraction(place_id)
    if not attraction:
        raise AttractionNotFoundError()
    return JSONResponse(content=attraction)


@router.get("/by_coordinates")
def get_attraction_by_coordinates(latitude: float, longitude: float):
    service = PlacesService()
    place_id = service.get_place_id_from_coordinates(latitude, longitude)
    if not place_id:
        raise PlaceNotFoundError(f"{latitude} - {longitude}")

    attraction = service.get_tourist_attraction(place_id)
    if not attraction:
        raise AttractionNotFoundError()
    return JSONResponse(content=attraction)