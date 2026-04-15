from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from typing import Optional
from app.services.photos_service import PhotosService
from app.services.places_service import PlacesService
from app.services.storage_service import is_stored, get_storage_url, download_and_store
from app.core.exceptions import PlaceNotFoundError, ImageNotFoundError, PlaceIdMissingError
from app.core.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter(prefix="/images", tags=["Images"])
places_service = PlacesService()
photos_service = PhotosService()


@router.get("/place", response_class=PlainTextResponse)
async def get_url_image_by_name(place: str):
    logger.info(f"HTTP | GET /images/place — place={place}")
    service = PhotosService()
    url = await service.get_image_by_name(place)
    if not url:
        logger.warning(f"HTTP | GET /images/place — image introuvable place={place}")
        raise ImageNotFoundError()
    logger.info(f"HTTP | GET /images/place — succès place={place}")
    return url


@router.get("/place_and_address", response_class=PlainTextResponse)
async def get_url_image_by_name_and_address(place_name: str, address: Optional[str] = None):
    logger.info(f"HTTP | GET /images/place_and_address — place={place_name} address={address}")
    place_id = await places_service.get_place_id(place_name, address)  # ← await ajouté
    if not place_id:
        logger.warning(f"HTTP | place_id introuvable — place={place_name}")
        raise PlaceNotFoundError(place_name)
    if is_stored(place_id):
        storage_url = get_storage_url(place_id)
        logger.info(f"STORAGE | ✅ Image en cache — Google Photos non appelé — place={place_name} place_id={place_id} url={storage_url}")
        return storage_url
    logger.info(f"STORAGE | ❌ Image absente du cache — appel Google Photos — place={place_name} place_id={place_id}")
    google_url = await photos_service.get_image_by_place_id(place_id)
    if not google_url:
        logger.warning(f"HTTP | image Google introuvable — place_id={place_id}")
        raise ImageNotFoundError()
    storage_url = await download_and_store(place_id, google_url)
    if not storage_url:
        raise ImageNotFoundError()
    logger.info(f"HTTP | ✅ Succès — place={place_name} place_id={place_id} url={storage_url}")
    return storage_url


@router.get("/id", response_class=PlainTextResponse)
async def get_url_image_by_id(place_id: str):
    logger.info(f"HTTP | GET /images/id — place_id={place_id}")
    if not place_id:
        logger.warning("HTTP | place_id manquant")
        raise PlaceIdMissingError()
    # 1️⃣ Image déjà stockée ? → retourne l'URL directement sans appel Google Photos
    if is_stored(place_id):
        storage_url = get_storage_url(place_id)
        logger.info(f"STORAGE | ✅ Image en cache — Google Photos non appelé — place_id={place_id} url={storage_url}")
        return storage_url
    # 2️⃣ Cache miss → récupère l'URL Google Photos
    logger.info(f"STORAGE | ❌ Image absente du cache — appel Google Photos — place_id={place_id}")
    google_url = await photos_service.get_image_by_place_id(place_id)
    if not google_url:
        logger.warning(f"HTTP | image Google introuvable — place_id={place_id}")
        raise ImageNotFoundError()
    # 3️⃣ Télécharge depuis Google → stocke → retourne l'URL propre
    storage_url = await download_and_store(place_id, google_url)
    if not storage_url:
        raise ImageNotFoundError()
    logger.info(f"HTTP | ✅ Succès — place_id={place_id} url={storage_url}")
    return storage_url