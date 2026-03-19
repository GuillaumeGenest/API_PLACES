import requests
import os
from dotenv import load_dotenv
from enum import Enum
from typing import List, Optional
from app.core.config import *
from app.core.logger import setup_logger
logger = setup_logger(__name__)

WIKIPEDIA_HEADERS = {
    "User-Agent": "PlacesApp/1.0 (contact@tonapp.com)"
}

GOOGLE_API_KEY = get_api_key()


def fetch_wikipedia_image(lang: str, query: str) -> str:
    search_url = f"https://{lang}.wikipedia.org/w/api.php"
    logger.debug(f"WIKIPEDIA | Recherche image — lang={lang} query={query}")

    # Recherche de la page
    search_response = requests.get(search_url, headers=WIKIPEDIA_HEADERS, params={
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json",
        "srlimit": 1
    })

    if not search_response.text:
        logger.warning(f"WIKIPEDIA | Réponse vide — lang={lang} query={query}")
        return None

    results = search_response.json().get("query", {}).get("search", [])
    if not results:
        logger.debug(f"WIKIPEDIA | Aucun résultat — lang={lang} query={query}")
        return None

    page_title = results[0]["title"]
    logger.debug(f"WIKIPEDIA | Page trouvée — title={page_title}")

    # Récupération de l'image
    image_response = requests.get(search_url, headers=WIKIPEDIA_HEADERS, params={
        "action": "query",
        "titles": page_title,
        "prop": "pageimages",
        "pithumbsize": 800,
        "format": "json"
    })
    if not image_response.text:
        logger.warning(f"WIKIPEDIA | Réponse vide pour l'image — lang={lang} title={page_title}")
        return None
    pages = image_response.json().get("query", {}).get("pages", {})
    for page in pages.values():
        thumbnail = page.get("thumbnail", {})
        if thumbnail:
            logger.info(f"WIKIPEDIA | Image trouvée — lang={lang} query={query} url={thumbnail['source']}")
            return thumbnail["source"]
    return None


def get_url_image_from_wikipedia(place_name: str, language: str = "fr") -> str:
    logger.info(f"WIKIPEDIA | Recherche image — place={place_name} lang={language}")
    url = fetch_wikipedia_image(language, place_name)
    if url:
        return url
    if language != "en":
        logger.debug(f"WIKIPEDIA | Fallback en anglais — place={place_name}")
        url = fetch_wikipedia_image("en", place_name)
        if url:
            return url
    logger.warning(f"WIKIPEDIA | Aucune image trouvée — place={place_name}")
    return None

def get_url_image_from_google(place_id: str) -> str:
    logger.info(f"GOOGLE | Recherche image — place_id={place_id}")
    url = f"https://places.googleapis.com/v1/places/{place_id}"
    fields = ["photos"]
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_API_KEY,
        "X-Goog-FieldMask": ",".join(fields),
        "Accept-Language": "fr"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        photos = data.get("photos", [])
        if photos:
            photo_name = photos[0]["name"]
            photo_url = f"https://places.googleapis.com/v1/{photo_name}/media?maxWidthPx=800&key={GOOGLE_API_KEY}"
            logger.info(f"GOOGLE | Image trouvée — place_id={place_id}")
            return photo_url

        logger.warning(f"GOOGLE | Aucune photo disponible — place_id={place_id}")
        return None

    except requests.exceptions.HTTPError as e:
        logger.error(f"GOOGLE | Erreur HTTP — place_id={place_id} status={response.status_code} error={e}")
        return None
    except Exception as e:
        logger.error(f"GOOGLE | Erreur inattendue — place_id={place_id} error={e}")
        return None