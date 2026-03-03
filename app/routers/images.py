from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from typing import Optional
from app.services.photos_service import PhotosService
from app.services.places_service import PlacesService
from app.core.exceptions import PlaceNotFoundError, ImageNotFoundError, PlaceIdMissingError
from app.core.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/images", tags=["Images"])

@router.get("/place", response_class=PlainTextResponse)
def get_url_image_by_name(place: str):
    logger.info(f"HTTP | GET /images/place — place={place}")
    service = PhotosService()

    url = service.get_image_by_name(place)
    if not url:
        logger.warning(f"HTTP | GET /images/place — image introuvable place={place}")
        raise ImageNotFoundError()

    logger.info(f"HTTP | GET /images/place — succès place={place}")
    return url


@router.get("/place_and_address", response_class=PlainTextResponse)
def get_url_image_by_name_and_address(place_name: str, address: Optional[str] = None):
    logger.info(f"HTTP | GET /images/place_and_address — place={place_name} address={address}")
    places_service = PlacesService()
    photos_service = PhotosService()

    place_id = places_service.get_place_id(place_name, address)
    if not place_id:
        logger.warning(f"HTTP | GET /images/place_and_address — place_id introuvable place={place_name}")
        raise PlaceNotFoundError(place_name)

    url = photos_service.get_image_by_place_id(place_id)
    if not url:
        logger.warning(f"HTTP | GET /images/place_and_address — image introuvable place_id={place_id}")
        raise ImageNotFoundError()

    logger.info(f"HTTP | GET /images/place_and_address — succès place={place_name} place_id={place_id}")
    return url


@router.get("/id", response_class=PlainTextResponse)
def get_url_image_by_id(place_id: str):
    logger.info(f"HTTP | GET /images/id — place_id={place_id}")

    if not place_id:
        logger.warning("HTTP | GET /images/id — place_id manquant")
        raise PlaceIdMissingError()

    service = PhotosService()
    url = service.get_image_by_place_id(place_id)
    if not url:
        logger.warning(f"HTTP | GET /images/id — image introuvable place_id={place_id}")
        raise ImageNotFoundError()

    logger.info(f"HTTP | GET /images/id — succès place_id={place_id}")
    return url