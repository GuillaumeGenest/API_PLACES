from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.services.places_service import PlacesService
from app.core.exceptions import PlaceNotFoundError, AttractionNotFoundError
from app.core.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/attraction", tags=["Attraction"])

@router.get("/by_name")
def get_attraction_by_name(place_name: str, address: str):
    logger.info(f"HTTP | GET /attraction/by_name — place={place_name} address={address}")
    service = PlacesService()

    place_id = service.get_place_id(place_name, address)
    if not place_id:
        logger.warning(f"HTTP | GET /attraction/by_name — place_id introuvable place={place_name}")
        raise PlaceNotFoundError(place_name)

    attraction = service.get_tourist_attraction(place_id)
    if not attraction:
        logger.error(f"HTTP | GET /attraction/by_name — attraction introuvable place_id={place_id}")
        raise AttractionNotFoundError()

    logger.info(f"HTTP | GET /attraction/by_name — succès place={place_name} place_id={place_id}")
    return JSONResponse(content=attraction)


@router.get("/by_coordinates")
def get_attraction_by_coordinates(latitude: float, longitude: float):
    logger.info(f"HTTP | GET /attraction/by_coordinates — lat={latitude} lng={longitude}")
    service = PlacesService()

    place_id = service.get_place_id_from_coordinates(latitude, longitude)
    if not place_id:
        logger.warning(f"HTTP | GET /attraction/by_coordinates — place_id introuvable lat={latitude} lng={longitude}")
        raise PlaceNotFoundError(f"{latitude} - {longitude}")

    attraction = service.get_tourist_attraction(place_id)
    if not attraction:
        logger.error(f"HTTP | GET /attraction/by_coordinates — attraction introuvable place_id={place_id}")
        raise AttractionNotFoundError()

    logger.info(f"HTTP | GET /attraction/by_coordinates — succès lat={latitude} lng={longitude} place_id={place_id}")
    return JSONResponse(content=attraction)