import os
import httpx
from typing import Optional
from app.core.config import get_server_base_url
from app.core.logger import setup_logger

logger = setup_logger(__name__)

STORAGE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "images", "storage", "caches")
os.makedirs(STORAGE_DIR, exist_ok=True)

def get_storage_path(place_id: str) -> str:
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
    try:
        logger.info(f"STORAGE | Téléchargement — place_id={place_id}")

        async with httpx.AsyncClient() as client:
            response = await client.get(google_url, follow_redirects=True)
            response.raise_for_status()
            image_bytes = response.content

        path = get_storage_path(place_id)
        with open(path, "wb") as f:
            f.write(image_bytes)

        storage_url = get_storage_url(place_id)
        logger.info(f"STORAGE | Sauvegardé — place_id={place_id} url={storage_url}")
        return storage_url

    except Exception as e:
        logger.error(f"STORAGE | Erreur — place_id={place_id} error={e}")
        return None