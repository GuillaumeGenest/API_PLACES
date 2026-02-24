from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from typing import Optional
from app.services.photos_service import PhotosService
from app.services.places_service import PlacesService
from app.core.exceptions import PlaceNotFoundError, ImageNotFoundError, PlaceIdMissingError

router = APIRouter(prefix="/images", tags=["Images"])

# /images/place  →  ancien /generate_url_image/place
@router.get("/place", response_class=PlainTextResponse)
def get_url_image_by_name(place: str):
    service = PhotosService()
    url = service.get_image_by_name(place)
    if not url:
        raise ImageNotFoundError()
    return url


# /images/place_and_address  →  ancien /get_url_image/place_and_address
@router.get("/place_and_address", response_class=PlainTextResponse)
def get_url_image_by_name_and_address(place_name: str, address: Optional[str] = None):
    places_service = PlacesService()
    photos_service = PhotosService()

    place_id = places_service.get_place_id(place_name, address)
    if not place_id:
        raise PlaceNotFoundError(place_name)

    url = photos_service.get_image_by_place_id(place_id)
    if not url:
        raise ImageNotFoundError()
    return url


# /images/id  →  ancien /get_url_image/id
@router.get("/id", response_class=PlainTextResponse)
def get_url_image_by_id(place_id: str):
    if not place_id:
        raise PlaceIdMissingError()

    service = PhotosService()
    url = service.get_image_by_place_id(place_id)
    if not url:
        raise ImageNotFoundError()
    return url