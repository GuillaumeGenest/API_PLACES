from fastapi import APIRouter, Depends
from app.services.places_service import PlacesService
from app.core.exceptions import PlaceNotFoundError, AttractionNotFoundError
from app.core.logger import setup_logger
from app.core.security import get_current_user
from app.models.attraction import SingleAttractionResponse
from typing import Optional
logger = setup_logger(__name__)
router = APIRouter(prefix="/attraction", tags=["Attraction"])


@router.get("/by_name", response_model=SingleAttractionResponse)
async def get_attraction_by_name(
    place_name: str,
    address: str,
    session_token: Optional[str] = None,
    user: dict = Depends(get_current_user)
):
    logger.info(
        f"HTTP | GET /attraction/by_name — place={place_name} address={address} "
        f"session_token={session_token}"
    )
    service = PlacesService()
    place_id = await service.get_place_id(place_name, address)
    if not place_id:
        logger.warning(f"HTTP | GET /attraction/by_name — place_id introuvable place={place_name}")
        raise PlaceNotFoundError(place_name)
    attraction = await service.get_tourist_attraction(place_id, session_token=session_token, user_id=user["sub"])
    if not attraction:
        logger.error(f"HTTP | GET /attraction/by_name — attraction introuvable place_id={place_id}")
        raise AttractionNotFoundError()
    logger.info(f"HTTP | GET /attraction/by_name — succès place={place_name} place_id={place_id}")
    return attraction


@router.get("/by_coordinates", response_model=SingleAttractionResponse)
async def get_attraction_by_coordinates(
    latitude: float,
    longitude: float,
    user: dict = Depends(get_current_user)
):
    logger.info(f"HTTP | GET /attraction/by_coordinates — lat={latitude} lng={longitude}")
    service = PlacesService()
    place_id = await service.get_place_id_from_coordinates(latitude, longitude)
    if not place_id:
        logger.warning(f"HTTP | GET /attraction/by_coordinates — place_id introuvable lat={latitude} lng={longitude}")
        raise PlaceNotFoundError(f"{latitude} - {longitude}")
    attraction = await service.get_tourist_attraction(place_id, user_id=user["sub"])
    if not attraction:
        logger.error(f"HTTP | GET /attraction/by_coordinates — attraction introuvable place_id={place_id}")
        raise AttractionNotFoundError()
    logger.info(f"HTTP | GET /attraction/by_coordinates — succès lat={latitude} lng={longitude} place_id={place_id}")
    return attraction