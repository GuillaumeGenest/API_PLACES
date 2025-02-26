import requests
import os

from dotenv import load_dotenv
from enum import Enum
from typing import List, Optional
from config import *

# Définition des catégories selon les spécifications exactes
class AttractionCategory(str, Enum):
    touristique = "touristique"
    nature = "nature"
    restaurant = "restaurant"
    autre = "autre"

    """
    Retourne les types Google Places à inclure en fonction de la catégorie exacte demandée
    """

def get_included_types(category: AttractionCategory) -> List[str]:
    category_types = {
        AttractionCategory.touristique: [
            #"point_of_interest",
            #"museum",
            "tourist_attraction"
        ],
        AttractionCategory.nature: [
            "hiking_area",
            "park",
            "beach"
        ],
        AttractionCategory.restaurant: [
            "restaurant",
            "bar",
            "amusement_park"
        ]
    }
    return category_types[category]


# Récupérer la clé API de Google Places depuis les variables d'environnement
load_dotenv()
GOOGLE_API_KEY = get_api_key()
print(f"Clé API utilisée pour les tests: {GOOGLE_API_KEY}")  # Version simple
#"""
#    Obtient les coordonnées d'une ville en fonction de son nom.
#
#   :param city_name: Nom de la ville (ex : "Grenoble").
#    :param api_key: Clé API Google.
#    :return: Tuple contenant la latitude et la longitude de la ville, ou None si aucune donnée n'est trouvée.
#"""

def get_city_coordinates(city_name):
    response = requests.get(
        "https://maps.googleapis.com/maps/api/geocode/json",
        params={
            "address": city_name,
            "key": GOOGLE_API_KEY,
            "language": "fr"  # Résultats en français
        }
    )
    
    # Analyse des données JSON renvoyées par l'API
    data = response.json()
    if data['results']:
        location = data['results'][0]['geometry']['location']
        latitude = location['lat']
        longitude = location['lng']
        print(f"les coordonnées sont  latitude {latitude}, longitude {longitude}")
        return latitude, longitude
    else:
        print("Aucune coordonnée trouvée pour cette ville.")
        return None

#"""
#    Obtient l'ID d'un lieu à partir de son nom.
#
#   :param location: Nom du lieu (ex : "Grenoble") avec une adresse
#    :param api_key: Clé API Google.
#    :return: L'ID du lieu, ou None si aucune correspondance n'est trouvée.
#"""

def get_place_id(name, address=None):
    # Construire la requête en combinant le nom et l'adresse si disponible
    query = name
    if address:
        query = f"{name}, {address}"
    
    # Paramètres de l
    response = requests.get(
        "https://maps.googleapis.com/maps/api/place/findplacefromtext/json",
        params={
            "input": query,
            "inputtype": "textquery",
            "key": GOOGLE_API_KEY
        }
    )
    data = response.json()
    if 'candidates' in data and data['candidates']:
        place_id = data['candidates'][0]['place_id']
        return place_id
    else:
        print("Aucun ID trouvé pour ce lieu ou accès refusé.")
        return None

#"""
#    Récupère le place_id Google à partir de coordonnées géographiques en utilisant l'API Geocoding.
#  
#    Args:
#        lat (float): Latitude
#        lng (float): Longitude
#        
#    Returns:
#        str: place_id du lieu ou None en cas d'erreur
#    """

def get_place_id_from_coordinates(lat, lng):
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    
    params = {
        "latlng": f"{lat},{lng}",
        "key": GOOGLE_API_KEY  # Assurez-vous que cette variable est bien définie avant d'appeler la fonction
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Vérifie les erreurs HTTP
        data = response.json()
        
        if data['status'] == 'OK' and len(data['results']) > 0:
            # Vérifie s'il y a un place_id dans les résultats
            place_id = data['results'][0].get('place_id', None)
            if place_id:
                return place_id
            else:
                print(f"Aucun place_id trouvé dans la réponse.")
                return None
        else:
            print(f"Erreur dans la réponse de l'API. Status: {data['status']}, Détails: {data}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête à l'API Geocoding: {e}")
        return None


#"""
#    Recherche et Récupère les attractions touristiques dans un rayon de 5 km autour des coordonnées fournies.
#    :param lat: Latitude du lieu.
#    :param lng: Longitude du lieu.
#    :param radius: Rayon de recherche en mètres (par défaut 5000 m soit 5 km).
#    :return: Liste des attractions touristiques avec leurs informations. (place_id, name, address, rating, photo_url, user_ratings_total)
#"""
def get_tourist_attractions_nearby(lat, lng, category: AttractionCategory, radius=5000):
    url = "https://places.googleapis.com/v1/places:searchNearby"
    
    # Demander tous les champs nécessaires dans le FieldMask
    fields = [
        "places.id",
        "places.displayName",
        "places.location",
        "places.formattedAddress",
        "places.rating",
        "places.userRatingCount",
        "places.photos",
        "places.websiteUri",
        "places.googleMapsUri",
        "places.internationalPhoneNumber",
        "places.editorialSummary",
        "places.regularOpeningHours",
        "places.types"  # Ajout des types
    ]
    
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_API_KEY,
        "X-Goog-FieldMask": ",".join(fields),
        "Accept-Language": "fr"
    }
    
    payload = {
        #"maxResultCount": max_results,
        "rankPreference": "POPULARITY",
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": lat,
                    "longitude": lng
                },
                "radius": float(radius)
            }
        },
        "includedTypes": get_included_types(category)
    }
    
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        if response.status_code != 200:
            print(f"Erreur lors de la requête à l'API Places: {response.status_code}")
            return None
        
        # Formater les résultats
        formatted_attractions = []
        if 'places' in data:
            for place in data['places']:
                category_name = category.value if category else AttractionCategory.autre.value
                attraction = {
                    'name': place.get('displayName', {}).get('text', 'Non spécifié'),
                    'address': place.get('formattedAddress', 'Non spécifiée'),
                    'place_id': place.get('id', 'Non spécifié'),
                    'latitude': place.get('location', {}).get('latitude'),
                    'longitude': place.get('location', {}).get('longitude'),
                    'rating': place.get('rating', 'Non notée'),
                    'user_ratings_total': place.get('userRatingCount', 0),
                    'photo_urls': [],
                    'website': place.get('websiteUri', 'Non disponible'),
                    'google_maps_url': place.get('googleMapsUri', 'Non disponible'),
                    'phone': place.get('internationalPhoneNumber', 'Non disponible'),
                    'description': place.get('editorialSummary', {}).get('text'),
                    'opening_hours': place.get('regularOpeningHours', {}).get('weekdayDescriptions', None),
                    'category': category_name
                }
                # Construire les URL des photos si disponibles
                if 'photos' in place and len(place['photos']) > 0:
                    for photo in place['photos']:
                        photo_reference = photo.get('name')
                        if photo_reference:
                            photo_url = f"https://places.googleapis.com/v1/{photo_reference}/media?key={GOOGLE_API_KEY}&maxHeightPx=400&maxWidthPx=400"
                            attraction['photo_urls'].append(photo_url)
                formatted_attractions.append(attraction)
        return {"attraction": formatted_attractions}
    except requests.exceptions.HTTPError as http_err:
        print(f"Erreur HTTP lors de la requête à l'API Places: {http_err}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête à l'API Places: {e}")
        return None


#"""
#    Récupère les détails d'un lieu à partir de son ID Google Places.
#    
#    Args:
#        place_id (str): L'identifiant Google Places du lieu
#        
#    Returns:
#        dict: Les détails du lieu ou None en cas d'erreur
#    """

def get_tourist_attraction(place_id):
    url = f"https://places.googleapis.com/v1/places/{place_id}"
    
    fields = [
        "id",
        "displayName",
        "location",
        "formattedAddress",
        "rating",
        "userRatingCount",
        "photos",
        "websiteUri",
        "googleMapsUri",
        "internationalPhoneNumber",
        "editorialSummary",
        "regularOpeningHours",
        "types"
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
        attraction = {
                    'name': place.get('displayName', {}).get('text', 'Non spécifié'),
                    'address': place.get('formattedAddress', 'Non spécifiée'),
                    'place_id': place.get('id', 'Non spécifié'),
                    'latitude': place.get('location', {}).get('latitude'),
                    'longitude': place.get('location', {}).get('longitude'),
                    'rating': place.get('rating', 'Non notée'),
                    'user_ratings_total': place.get('userRatingCount', 0),
                    'photo_urls': [],
                    'website': place.get('websiteUri', 'Non disponible'),
                    'google_maps_url': place.get('googleMapsUri', 'Non disponible'),
                    'phone': place.get('internationalPhoneNumber', 'Non disponible'),
                    'description': place.get('editorialSummary', {}).get('text'),
                    'opening_hours': place.get('regularOpeningHours', {}).get('weekdayDescriptions', None),
                    'category': AttractionCategory.autre.value
        }
                # Construire les URL des photos si disponibles
        if 'photos' in place and len(place['photos']) > 0:
                    for photo in place['photos']:
                        photo_reference = photo.get('name')
                        if photo_reference:
                            photo_url = f"https://places.googleapis.com/v1/{photo_reference}/media?key={GOOGLE_API_KEY}&maxHeightPx=400&maxWidthPx=400"
                            attraction['photo_urls'].append(photo_url)
        return {"attraction": attraction}
        
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête à l'API Places: {e}")
        return None