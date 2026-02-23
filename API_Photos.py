import requests
import os

from dotenv import load_dotenv
from enum import Enum
from typing import List, Optional
from config import *


WIKIPEDIA_HEADERS = {
    "User-Agent": "PlacesApp/1.0 (contact@tonapp.com)"
}

# Récupérer la clé API de Google Places depuis les variables d'environnement
print("###############################################################")
print("API_PHOTOS")
print("###############################################################")
load_dotenv()
GOOGLE_API_KEY = get_api_key()
print(f"Clé API utilisée pour les tests: {GOOGLE_API_KEY}")


def fetch_wikipedia_image(lang: str, query: str) -> str:
    search_url = f"https://{lang}.wikipedia.org/w/api.php"
    
    # Recherche de la page
    search_response = requests.get(search_url, headers=WIKIPEDIA_HEADERS, params={
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json",
        "srlimit": 1
    })
    
    if not search_response.text:
        print(f"Réponse vide de Wikipedia ({lang})")
        return None
    
    results = search_response.json().get("query", {}).get("search", [])
    if not results:
        return None
    
    page_title = results[0]["title"]
    
    # Récupération de l'image
    image_response = requests.get(search_url, headers=WIKIPEDIA_HEADERS, params={
        "action": "query",
        "titles": page_title,
        "prop": "pageimages",
        "pithumbsize": 800,
        "format": "json"
    })
    
    if not image_response.text:
        print(f"Réponse vide pour l'image ({lang})")
        return None
    
    pages = image_response.json().get("query", {}).get("pages", {})
    for page in pages.values():
        thumbnail = page.get("thumbnail", {})
        if thumbnail:
            print(f"✅ Image Wikipedia trouvée ({lang}) pour '{query}': {thumbnail['source']}")
            return thumbnail["source"]
    
    return None


#get_wikipedia_photo_url

def get_url_image_from_wikipedia(place_name: str, language: str = "fr") -> str:
    url = fetch_wikipedia_image(language, place_name)
    if url:
        return url
    
    if language != "en":
        url = fetch_wikipedia_image("en", place_name)
        if url:
            return url
    
    print(f"❌ Aucune image Wikipedia trouvée pour '{place_name}'")
    return None

def get_url_image_from_google(place_id):
    url = f"https://places.googleapis.com/v1/places/{place_id}"
    
    fields = ["photos"]
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_API_KEY,
        "X-Goog-FieldMask": ",".join(fields),
        "Accept-Language": "fr"
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    
    photos = data.get("photos", [])
    if photos:
        photo_name = photos[0]["name"]
        # URL finale pour afficher la photo
        photo_url = f"https://places.googleapis.com/v1/{photo_name}/media?maxWidthPx=800&key={GOOGLE_API_KEY}"
        return photo_url
    
    return None