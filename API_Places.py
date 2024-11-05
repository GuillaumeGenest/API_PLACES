import requests
import os
import json
city_name = 'Grenoble'

# Récupérer la clé API de Google Places depuis les variables d'environnement
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise Exception("La clé API Google Places n'est pas configurée")

"""
    Obtient les coordonnées d'une ville en fonction de son nom.

    :param city_name: Nom de la ville (ex : "Grenoble").
    :param api_key: Clé API Google.
    :return: Tuple contenant la latitude et la longitude de la ville, ou None si aucune donnée n'est trouvée.
"""

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
        return latitude, longitude
    else:
        print("Aucune coordonnée trouvée pour cette ville.")
        return None


"""
    Obtient l'ID d'un lieu à partir de son nom.

    :param location: Nom du lieu (ex : "Grenoble").
    :param api_key: Clé API Google.
    :return: L'ID du lieu, ou None si aucune correspondance n'est trouvée.
"""

def get_place_id(location):
    response = requests.get(
        "https://maps.googleapis.com/maps/api/place/findplacefromtext/json",
        params={
            "input": location,
            "inputtype": "textquery",
            "key": GOOGLE_API_KEY
        }
    )
    
    data = response.json()
    if data['candidates']:
        place_id = data['candidates'][0]['place_id']
        return place_id
    else:
        print("Aucun ID trouvé pour ce lieu.")
        return None




"""
    Recherche et Récupère les attractions touristiques dans un rayon de 5 km autour des coordonnées fournies.
    :param lat: Latitude du lieu.
    :param lng: Longitude du lieu.
    :param radius: Rayon de recherche en mètres (par défaut 5000 m soit 5 km).
    :return: Liste des attractions touristiques avec leurs informations. (place_id, name, address, rating, photo_url, user_ratings_total)
"""




def get_tourist_attractions_nearby(lat, lng, radius=5000):
    url = "https://places.googleapis.com/v1/places:searchNearby"
    
    # Demander tous les champs nécessaires dans le FieldMask
    fields = [
        "places.id",
        "places.displayName",
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
        "includedTypes": [
            "hiking_area",     
            "tourist_attraction"
            ]
    }
    
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        
        # Formater les résultats
        formatted_attractions = []
        if 'places' in data:
            for place in data['places']:
                attraction = {
                    'name': place.get('displayName', {}).get('text', 'Non spécifié'),
                    'address': place.get('formattedAddress', 'Non spécifiée'),
                    'place_id': place.get('id', 'Non spécifié'),
                    'rating': place.get('rating', 'Non notée'),
                    'user_ratings_total': place.get('userRatingCount', 0),
                    'photo_urls': [],
                    'website': place.get('websiteUri', 'Non disponible'),
                    'google_maps_url': place.get('googleMapsUri', 'Non disponible'),
                    'phone': place.get('internationalPhoneNumber', 'Non disponible'),
                    'description': place.get('editorialSummary', {}).get('text'),
                    'opening_hours': place.get('regularOpeningHours', {}).get('weekdayDescriptions', None)
                }
                # Construire les URL des photos si disponibles
                if 'photos' in place and len(place['photos']) > 0:
                    for photo in place['photos']:
                        photo_reference = photo.get('name')
                        if photo_reference:
                            photo_url = f"https://places.googleapis.com/v1/{photo_reference}/media?key={GOOGLE_API_KEY}&maxHeightPx=400&maxWidthPx=400"
                            attraction['photo_urls'].append(photo_url)
                formatted_attractions.append(attraction)
        return formatted_attractions
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête à l'API Places: {e}")
        return None

