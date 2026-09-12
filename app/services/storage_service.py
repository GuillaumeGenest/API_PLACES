import os
import re
import httpx
from typing import Optional
from app.core.config import get_server_base_url
from app.core.exceptions import InvalidPlaceIdError
from app.core.logger import setup_logger

logger = setup_logger(__name__)

STORAGE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "images", "storage", "caches")
os.makedirs(STORAGE_DIR, exist_ok=True)

PLACE_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")
MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024  # 10 Mo

def get_storage_path(place_id: str) -> str:
    if not PLACE_ID_PATTERN.match(place_id):
        raise InvalidPlaceIdError(place_id)
    return os.path.join(STORAGE_DIR, f"{place_id}.jpg")

"""Retourne l'URL publique de l'image sur ton serveur"""
def get_storage_url(place_id: str) -> str:
    base_url = get_server_base_url()
    return f"{base_url}/images/storage/caches/{place_id}.jpg"

"""Vérifie si l'image est déjà stockée"""
def is_stored(place_id: str) -> bool:
    return os.path.exists(get_storage_path(place_id))

"""
    Télécharge l'image depuis Google et la stocke sur le serveur.
    Retourne l'URL publique de ton serveur.
"""
async def download_and_store(place_id: str, google_url: str) -> Optional[str]:
    path = get_storage_path(place_id)
    try:
        logger.info(f"STORAGE | Téléchargement — place_id={place_id}")

        async with httpx.AsyncClient() as client:
            async with client.stream("GET", google_url, follow_redirects=True) as response:
                response.raise_for_status()
                total = 0
                with open(path, "wb") as f:
                    async for chunk in response.aiter_bytes():
                        total += len(chunk)
                        if total > MAX_IMAGE_SIZE_BYTES:
                            f.close()
                            os.remove(path)
                            logger.error(
                                f"STORAGE | Image trop volumineuse (> {MAX_IMAGE_SIZE_BYTES} bytes) "
                                f"— place_id={place_id}"
                            )
                            return None
                        f.write(chunk)

        storage_url = get_storage_url(place_id)
        logger.info(f"STORAGE | Sauvegardé — place_id={place_id} url={storage_url}")
        return storage_url

    except Exception as e:
        logger.error(f"STORAGE | Erreur — place_id={place_id} error={e}")
        return None