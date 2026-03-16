import requests
import os
from dotenv import load_dotenv
from enum import Enum
from typing import List, Optional
from app.core.config import *
from app.core.logger import setup_logger
from app.api.API_Photos import get_url_image_from_wikipedia, get_url_image_from_google
from app.api.API_Places_AI import generate_description
from app.models.attraction import AttractionCategory
from app.services.storage_service import is_stored, get_storage_url, download_and_store

logger = setup_logger(__name__)

load_dotenv()
GOOGLE_API_KEY = get_api_key()

def get_included_types(category: AttractionCategory) -> List[str]:
    category_types = {
        AttractionCategory.touristique: ["tourist_attraction"],
        AttractionCategory.nature: ["hiking_area", "park", "beach"],
        AttractionCategory.restaurant: ["restaurant", "bar", "amusement_park"]
    }
    return category_types[category]


def get_city_coordinates(city_name):
    logger.info(f"GOOGLE | Recherche coordonnées — city={city_name}")
    try:
        response = requests.get(
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
    except requests.exceptions.RequestException as e:
        logger.error(f"GOOGLE | Erreur get_city_coordinates — city={city_name} error={e}")
        return None


def get_place_id_text_search_essentials(name, address=None):
    query = f"{name}, {address}" if address else name
    logger.info(f"GOOGLE | Recherche place_id (legacy) — query={query}")
    try:
        response = requests.get(
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
    except requests.exceptions.RequestException as e:
        logger.error(f"GOOGLE | Erreur get_place_id_text_search_essentials — query={query} error={e}")
        return None


def get_place_id(name, address=None):
    query = f"{name}, {address}" if address else name
    logger.info(f"GOOGLE | Recherche place_id — query={query}")
    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_API_KEY,
        "X-Goog-FieldMask": "places.id"
    }
    try:
        response = requests.post(url, json={"textQuery": query}, headers=headers)
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
    except requests.exceptions.RequestException as e:
        logger.error(f"GOOGLE | Erreur get_place_id — query={query} error={e}")
        return None


def get_place_name(name, address=None):
    query = f"{name}, {address}" if address else name
    logger.info(f"GOOGLE | Recherche place_name — query={query}")
    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_API_KEY,
        "X-Goog-FieldMask": "places.name"
    }
    try:
        response = requests.post(url, json={"textQuery": query}, headers=headers)
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
    except requests.exceptions.RequestException as e:
        logger.error(f"GOOGLE | Erreur get_place_name — query={query} error={e}")
        return None


def get_place_id_from_coordinates(lat, lng):
    logger.info(f"GOOGLE | Recherche place_id depuis coordonnées — lat={lat} lng={lng}")
    try:
        response = requests.get(
            "https://maps.googleapis.com/maps/api/geocode/json",
            params={"latlng": f"{lat},{lng}", "key": GOOGLE_API_KEY}
        )
        response.raise_for_status()
        data = response.json()
        if data['status'] == 'OK' and len(data['results']) > 0:
            place_id = data['results'][0].get('place_id')
            if place_id:
                logger.info(f"GOOGLE | place_id trouvé depuis coordonnées — lat={lat} lng={lng} place_id={place_id}")
                return place_id
            logger.warning(f"GOOGLE | Aucun place_id dans la réponse — lat={lat} lng={lng}")
            return None
        logger.warning(f"GOOGLE | Erreur réponse API — status={data['status']} lat={lat} lng={lng}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"GOOGLE | Erreur get_place_id_from_coordinates — lat={lat} lng={lng} error={e}")
        return None


def get_representative_place_id(city_name):
    logger.info(f"GOOGLE | Recherche place_id représentatif — city={city_name}")
    try:
        response = requests.get(
            "https://maps.googleapis.com/maps/api/place/textsearch/json",
            params={"query": f"attractions à visiter à {city_name}", "key": GOOGLE_API_KEY, "language": "fr"}
        )
        data = response.json()
        if "results" in data and data["results"]:
            place_id = data["results"][0]["place_id"]
            logger.info(f"GOOGLE | place_id représentatif trouvé — city={city_name} place_id={place_id}")
            return place_id
        logger.warning(f"GOOGLE | Aucun résultat représentatif — city={city_name}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"GOOGLE | Erreur get_representative_place_id — city={city_name} error={e}")
        return None


def get_tourist_attractions_nearby(lat, lng, category: AttractionCategory, radius=5000):
    logger.info(f"GOOGLE | Recherche attractions — lat={lat} lng={lng} category={category.value} radius={radius}")
    url = "https://places.googleapis.com/v1/places:searchNearby"
    fields = [
        "places.id", "places.displayName", "places.location",
        "places.formattedAddress", "places.rating", "places.userRatingCount",
        "places.websiteUri", "places.googleMapsUri", "places.internationalPhoneNumber",
        "places.editorialSummary", "places.regularOpeningHours",
        "priceLevel", "priceRange", "places.types"
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
    try:
        response = requests.post(url, headers=headers, json=payload)
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
                photo_url = get_url_image_from_wikipedia(f"{name} {address}")
                attraction = {
                    'name': name,
                    'address': address,
                    'place_id': place.get('id', 'Non spécifié'),
                    'latitude': place.get('location', {}).get('latitude'),
                    'longitude': place.get('location', {}).get('longitude'),
                    'rating': place.get('rating', 'Non notée'),
                    'user_ratings_total': place.get('userRatingCount', 0),
                    'photo_urls': [photo_url] if photo_url else [],
                    'website': place.get('websiteUri', 'Non disponible'),
                    'google_maps_url': place.get('googleMapsUri', 'Non disponible'),
                    'phone': place.get('internationalPhoneNumber', 'Non disponible'),
                    'description': place.get('editorialSummary', {}).get('text'),
                    'opening_hours': place.get('regularOpeningHours', {}).get('weekdayDescriptions'),
                    'price_level': place.get('priceLevel', "Non disponible"),
                    'price_range': place.get('priceRange', "Non disponible"),
                    'category': category_name
                }
                formatted_attractions.append(attraction)
        else:
            logger.warning(f"GOOGLE | Aucune attraction trouvée — lat={lat} lng={lng}")

        return {"attraction": formatted_attractions}

    except requests.exceptions.HTTPError as e:
        logger.error(f"GOOGLE | Erreur HTTP get_tourist_attractions_nearby — status={response.status_code} error={e}")
        return {"attraction": []}
    except requests.exceptions.RequestException as e:
        logger.error(f"GOOGLE | Erreur get_tourist_attractions_nearby — error={e}")
        return {"attraction": []}


async def get_tourist_attraction(place_id: str):
    logger.info(f"GOOGLE | Récupération attraction — place_id={place_id}")
    url = f"https://places.googleapis.com/v1/places/{place_id}"
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
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        place = response.json()
        logger.debug(f"GOOGLE | Réponse brute — place_id={place_id} data={place}")

        name = place.get('displayName', {}).get('text', 'Non spécifié')
        address = place.get('formattedAddress', 'Non spécifiée')

        logger.debug(f"OPENAI | Génération description — name={name}")
        description = generate_description(name, full_address=address)

        # ─── Photo avec cache ─────────────────────────────────
        logger.debug(f"GOOGLE | Récupération photo — place_id={place_id}")
        if is_stored(place_id):
            photo_url = get_storage_url(place_id)
            logger.info(f"STORAGE | ✅ Cache hit — place_id={place_id}")
        else:
            logger.info(f"STORAGE | ❌ Cache miss — appel Google Photos — place_id={place_id}")
            google_url = get_url_image_from_google(place_id)
            if google_url:
                photo_url = await download_and_store(place_id, google_url)
            else:
                photo_url = None
        # ──────────────────────────────────────────────────────

        attraction = {
            'name': name,
            'address': address,
            'place_id': place.get('id', 'Non spécifié'),
            'latitude': place.get('location', {}).get('latitude'),
            'longitude': place.get('location', {}).get('longitude'),
            'rating': place.get('rating', 'Non notée'),
            'user_ratings_total': place.get('userRatingCount', 0),
            'photo_urls': [photo_url] if photo_url else [],
            'website': place.get('websiteUri', 'Non disponible'),
            'google_maps_url': place.get('googleMapsUri', 'Non disponible'),
            'phone': place.get('internationalPhoneNumber', 'Non disponible'),
            'description': description,
            'opening_hours': place.get('regularOpeningHours', {}).get('weekdayDescriptions'),
            'price_level': place.get('priceLevel', "Non disponible"),
            'price_range': place.get('priceRange', "Non disponible"),
            'category': AttractionCategory.autre.value
        }
        logger.info(f"GOOGLE | Attraction récupérée — name={name} place_id={place_id}")
        return {"attraction": attraction}

    except requests.exceptions.RequestException as e:
        logger.error(f"GOOGLE | Erreur get_tourist_attraction — place_id={place_id} error={e}")
        return None