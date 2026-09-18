import httpx
import uuid
import os
from dotenv import load_dotenv
from enum import Enum
from typing import List, Optional
from starlette.concurrency import run_in_threadpool
from app.core.config import *
from app.core.logger import setup_logger
from app.api.API_Photos import get_url_image_from_wikipedia, get_url_image_from_google
from app.models.attraction import AttractionCategory
from app.services.ai_service import AIService
from app.services.storage_service import is_stored, get_storage_url, download_and_store
from app.services.supabase_service import get_attraction_by_place_id, save_attraction

logger = setup_logger(__name__)

GOOGLE_API_KEY = get_api_key()

def get_included_types(category: AttractionCategory) -> List[str]:
    category_types = {
        AttractionCategory.touristique: ["tourist_attraction"],
        AttractionCategory.nature: ["hiking_area", "park", "beach"],
        AttractionCategory.restaurant: ["restaurant", "bar", "amusement_park"]
    }
    return category_types[category]


async def get_city_coordinates(city_name):
    logger.info(f"GOOGLE | Recherche coordonnées — city={city_name}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://maps.googleapis.com/maps/api/geocode/json",
                params={
                    "address": city_name,
                    "key": GOOGLE_API_KEY,
                    "language": "fr"
                }
            )
        data = response.json()
        if data['results']:
            location = data['results'][0]['geometry']['location']
            lat, lng = location['lat'], location['lng']
            logger.info(f"GOOGLE | Coordonnées trouvées — city={city_name} lat={lat} lng={lng}")
            return lat, lng
        else:
            logger.warning(f"GOOGLE | Aucune coordonnée trouvée — city={city_name}")
            return None
    except httpx.HTTPError as e:
        logger.error(f"GOOGLE | Erreur get_city_coordinates — city={city_name} error={e}")
        return None


def format_price_range(price_range):
    if not price_range:
        return None
    start = price_range.get("startPrice", {}).get("units")
    end = price_range.get("endPrice", {}).get("units")
    if start is not None and end is not None:
        return f"{start} - {end}"
    return None


async def get_place_id_text_search_essentials(name, address=None):
    query = f"{name}, {address}" if address else name
    logger.info(f"GOOGLE | Recherche place_id (legacy) — query={query}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://maps.googleapis.com/maps/api/place/findplacefromtext/json",
                params={"input": query, "inputtype": "textquery", "key": GOOGLE_API_KEY}
            )
        data = response.json()
        if 'candidates' in data and data['candidates']:
            place_id = data['candidates'][0]['place_id']
            logger.info(f"GOOGLE | place_id trouvé — query={query} place_id={place_id}")
            return place_id
        logger.warning(f"GOOGLE | Aucun place_id trouvé — query={query}")
        return None
    except httpx.HTTPError as e:
        logger.error(f"GOOGLE | Erreur get_place_id_text_search_essentials — query={query} error={e}")
        return None


async def get_place_id(name, address=None):
    query = f"{name}, {address}" if address else name
    logger.info(f"GOOGLE | Recherche place_id — query={query}")
    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_API_KEY,
        "X-Goog-FieldMask": "places.id"
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json={"textQuery": query}, headers=headers)
        if response.status_code != 200:
            logger.error(f"GOOGLE | Erreur API place_id — query={query} status={response.status_code}")
            return None
        data = response.json()
        if "places" in data and len(data["places"]) > 0:
            place_id = data["places"][0]['id']
            logger.info(f"GOOGLE | place_id trouvé — query={query} place_id={place_id}")
            return place_id
        logger.warning(f"GOOGLE | Aucun place_id trouvé — query={query}")
        return None
    except httpx.HTTPError as e:
        logger.error(f"GOOGLE | Erreur get_place_id — query={query} error={e}")
        return None


async def get_place_name(name, address=None):
    query = f"{name}, {address}" if address else name
    logger.info(f"GOOGLE | Recherche place_name — query={query}")
    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_API_KEY,
        "X-Goog-FieldMask": "places.name"
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json={"textQuery": query}, headers=headers)
        if response.status_code != 200:
            logger.error(f"GOOGLE | Erreur API place_name — query={query} status={response.status_code}")
            return None
        data = response.json()
        if "places" in data and len(data["places"]) > 0:
            place_name = data["places"][0]['name']
            logger.info(f"GOOGLE | place_name trouvé — query={query} name={place_name}")
            return place_name
        logger.warning(f"GOOGLE | Aucun place_name trouvé — query={query}")
        return None
    except httpx.HTTPError as e:
        logger.error(f"GOOGLE | Erreur get_place_name — query={query} error={e}")
        return None


async def get_place_id_from_coordinates(lat, lng):
    logger.info(f"GOOGLE | Recherche place_id depuis coordonnées — lat={lat} lng={lng}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://maps.googleapis.com/maps/api/geocode/json",
                params={"latlng": f"{lat},{lng}", "key": GOOGLE_API_KEY}
            )
        data = response.json()
        if data['status'] == 'OK' and len(data['results']) > 0:
            place_id = data['results'][0].get('place_id')
            if place_id:
                logger.info(f"GOOGLE | place_id trouvé depuis coordonnées — lat={lat} lng={lng} place_id={place_id}")
                return place_id
        logger.warning(f"GOOGLE | Aucun place_id trouvé — lat={lat} lng={lng}")
        return None
    except httpx.HTTPError as e:
        logger.error(f"GOOGLE | Erreur get_place_id_from_coordinates — lat={lat} lng={lng} error={e}")
        return None


async def get_representative_place_id(city_name):
    logger.info(f"GOOGLE | Recherche place_id représentatif — city={city_name}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://maps.googleapis.com/maps/api/place/textsearch/json",
                params={
                    "query": f"attractions à visiter à {city_name}",
                    "key": GOOGLE_API_KEY,
                    "language": "fr"
                }
            )
        data = response.json()
        if "results" in data and data["results"]:
            place_id = data["results"][0]["place_id"]
            logger.info(f"GOOGLE | place_id représentatif trouvé — city={city_name} place_id={place_id}")
            return place_id
        return None
    except httpx.HTTPError as e:
        logger.error(f"GOOGLE | Erreur get_representative_place_id — city={city_name} error={e}")
        return None


async def get_tourist_attractions_nearby(lat, lng, category: AttractionCategory, radius=5000):
    logger.info(f"GOOGLE | Recherche attractions — lat={lat} lng={lng} category={category.value} radius={radius}")
    url = "https://places.googleapis.com/v1/places:searchNearby"
    fields = [
        "places.id", "places.displayName", "places.location",
        "places.formattedAddress", "places.rating", "places.userRatingCount",
        "places.websiteUri", "places.googleMapsUri", "places.internationalPhoneNumber",
        "places.editorialSummary", "places.regularOpeningHours",
        "places.priceLevel", "places.priceRange", "places.types"
    ]
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_API_KEY,
        "X-Goog-FieldMask": ",".join(fields),
        "Accept-Language": "fr"
    }
    payload = {
        "maxResultCount": 10,
        "rankPreference": "POPULARITY",
        "locationRestriction": {
            "circle": {"center": {"latitude": lat, "longitude": lng}, "radius": float(radius)}
        },
        "includedTypes": get_included_types(category)
    }
    logger.debug(f"GOOGLE | Payload envoyé — {payload}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
        data = response.json()
        formatted_attractions = []

        if 'places' in data:
            logger.info(f"GOOGLE | {len(data['places'])} attractions trouvées — lat={lat} lng={lng}")
            for place in data['places']:
                category_name = category.value if category else AttractionCategory.autre.value
                name = place.get('displayName', {}).get('text', 'Non spécifié')
                address = place.get('formattedAddress', 'Non spécifiée')
                logger.debug(f"WIKIPEDIA | Recherche image — name={name}")
                photo_url = await get_url_image_from_wikipedia(f"{name} {address}")
                attraction = {
                    'id': str(uuid.uuid4()),
                    'name': name,
                    'address': address,
                    'place_id': place.get('id'),
                    'latitude': place.get('location', {}).get('latitude'),
                    'longitude': place.get('location', {}).get('longitude'),
                    'rating': place.get('rating'),
                    'user_ratings_total': place.get('userRatingCount', 0),
                    'photo_urls': [photo_url] if photo_url else [],
                    'website': place.get('websiteUri'),
                    'google_maps_url': place.get('googleMapsUri'),
                    'phone': place.get('internationalPhoneNumber'),
                    'description': place.get('editorialSummary', {}).get('text'),
                    'opening_hours': place.get('regularOpeningHours', {}).get('weekdayDescriptions'),
                    'price_level': place.get('priceLevel'),
                    'price_range': format_price_range(place.get('priceRange')),
                    'category': category_name
                }
                formatted_attractions.append(attraction)
        else:
            logger.warning(f"GOOGLE | Aucune attraction trouvée — lat={lat} lng={lng}")

        return {"attraction": formatted_attractions}

    except httpx.HTTPError as e:
        logger.error(f"GOOGLE | Erreur HTTP get_tourist_attractions_nearby — error={e}")
        return {"attraction": []}


async def get_tourist_attraction(
    place_id: str,
    session_token: Optional[str] = None,
    user_id: Optional[str] = None
):
    logger.info(f"GOOGLE | Récupération attraction — place_id={place_id}")

    # ─── 1. Checker Supabase ──────────────────────────────────────
    cached = await run_in_threadpool(get_attraction_by_place_id, place_id)
    if cached:
        logger.info(f"SUPABASE | ✅ Attraction trouvée — place_id={place_id}")
        return {"attraction": cached}

    # ─── 2. Cache miss → appeler Google API ──────────────────────
    logger.info(f"SUPABASE | ❌ Attraction non trouvée — appel Google API — place_id={place_id}")
    url = f"https://places.googleapis.com/v1/places/{place_id}"

    params = {}
    if session_token:
        params["sessionToken"] = session_token

    fields = [
        "id", "displayName", "location", "formattedAddress",
        "rating", "userRatingCount", "photos", "websiteUri",
        "googleMapsUri", "internationalPhoneNumber",
        "regularOpeningHours", "priceLevel", "priceRange", "types"
    ]
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_API_KEY,
        "X-Goog-FieldMask": ",".join(fields),
        "Accept-Language": "fr"
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
        place = response.json()
        logger.debug(f"GOOGLE | Réponse brute — place_id={place_id} data={place}")

        name = place.get('displayName', {}).get('text', 'Non spécifié')
        address = place.get('formattedAddress', None)

        logger.debug(f"OPENAI | Génération description — name={name}")
        description = await AIService().generate_description(name, address, user_id=user_id)

        # ─── Photo avec cache ─────────────────────────────────
        logger.debug(f"GOOGLE | Récupération photo — place_id={place_id}")
        if is_stored(place_id):
            photo_url = get_storage_url(place_id)
            logger.info(f"STORAGE | ✅ Cache hit — place_id={place_id}")
        else:
            logger.info(f"STORAGE | ❌ Cache miss — appel Google Photos — place_id={place_id}")
            google_url = await get_url_image_from_google(place_id)
            if google_url:
                photo_url = await download_and_store(place_id, google_url)
            else:
                photo_url = None

        raw_rating = place.get('rating')
        try:
            rating = float(raw_rating) if raw_rating is not None else None
        except (ValueError, TypeError):
            rating = None

        attraction = {
            'id': str(uuid.uuid4()),
            'name': name,
            'address': address,
            'place_id': place.get('id', None),
            'latitude': place.get('location', {}).get('latitude'),
            'longitude': place.get('location', {}).get('longitude'),
            'rating': rating,
            'user_ratings_total': place.get('userRatingCount', 0),
            'photo_urls': [photo_url] if photo_url else [],
            'website': place.get('websiteUri', None),
            'google_maps_url': place.get('googleMapsUri', None),
            'phone': place.get('internationalPhoneNumber', None),
            'description': description,
            'opening_hours': place.get('regularOpeningHours', {}).get('weekdayDescriptions'),
            'price_level': place.get('priceLevel', None),
            'price_range': format_price_range(place.get('priceRange')),
            'category': AttractionCategory.autre.value
        }
        await run_in_threadpool(save_attraction, attraction)
        logger.info(f"GOOGLE | Attraction récupérée — name={name} place_id={place_id}")
        return {"attraction": attraction}

    except httpx.HTTPError as e:
        logger.error(f"GOOGLE | Erreur get_tourist_attraction — place_id={place_id} error={e}")
        return None