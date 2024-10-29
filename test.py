import requests
import os
# Récupérer la clé API de Google Places depuis les variables d'environnement
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise Exception("La clé API Google Places n'est pas configurée")

city_name = 'Paris'



def get_city_coordinates(city_name):
    """
    Obtient les coordonnées d'une ville en fonction de son nom.

    :param city_name: Nom de la ville (ex : "Grenoble").
    :param api_key: Clé API Google.
    :return: Tuple contenant la latitude et la longitude de la ville, ou None si aucune donnée n'est trouvée.
    """
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




def get_place_id(location):
    """
    Obtient l'ID d'un lieu à partir de son nom.

    :param location: Nom du lieu (ex : "Grenoble").
    :param api_key: Clé API Google.
    :return: L'ID du lieu, ou None si aucune correspondance n'est trouvée.
    """
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

def get_coordinates_from_place_id(place_id):
    """
    Obtient les coordonnées (latitude et longitude) d'un lieu à partir de son ID.

    :param place_id: L'ID du lieu obtenu avec la fonction get_place_id.
    :param api_key: Clé API Google.
    :return: Tuple contenant la latitude et la longitude du lieu, ou None si les coordonnées ne sont pas trouvées.
    """
    response = requests.get(
        "https://maps.googleapis.com/maps/api/place/details/json",
        params={
            "place_id": place_id,
            "fields": "geometry",
            "key": GOOGLE_API_KEY
        }
    )

    data = response.json()
    if "result" in data and "geometry" in data["result"]:
        location = data["result"]["geometry"]["location"]
        latitude = location["lat"]
        longitude = location["lng"]
        return latitude, longitude
    else:
        print("Les coordonnées n'ont pas pu être obtenues pour cet ID.")
        return None
    


def get_tourist_attractions_nearby(lat, lng, radius=5000):
    """
    Récupère les attractions touristiques dans un rayon de 5 km autour des coordonnées fournies.
    :param lat: Latitude du lieu.
    :param lng: Longitude du lieu.
    :param radius: Rayon de recherche en mètres (par défaut 5000 m soit 5 km).
    :return: Liste des attractions touristiques avec leurs informations.
    """
    response = requests.get(
        "https://maps.googleapis.com/maps/api/place/nearbysearch/json",
        params={
            "location": f"{lat},{lng}",
            "radius": radius,
            "rankby": "prominence",
            "type": "tourist_attraction",
            #"fields": "name,vicinity,place_id,rating,photos,editorial_summary,website_uri,url",
            "key": GOOGLE_API_KEY,
            "language": "fr"  # Résultats en français
        }
    )
    data = response.json()
    if data['status'] == 'OK':
        attractions = data['results'][:10]
        results = []
        for attraction in attractions:
            # Extraction des informations principales
            name = attraction.get("name", "Nom non disponible")
            address = attraction.get("vicinity", "Adresse non disponible")
            place_id = attraction.get("place_id", "ID non disponible")
            rating = attraction.get("rating", "Note non disponible")
            website_uri = attraction.get("website_uri", "Site web non disponible")
            google_maps_uri = attraction.get("url", "Lien Google Maps non disponible")

            # Récupération de la photo si disponible
            photo_url = None
            if "photos" in attraction:
                photo_reference = attraction["photos"][0]["photo_reference"]
                photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_reference}&key={GOOGLE_API_KEY}"

            # Appel supplémentaire à Place Details pour obtenir la description
           #details_response = requests.get(
           #     "https://maps.googleapis.com/maps/api/place/details/json",
           #     params={
           #         "place_id": place_id,
            #        "fields": "editorial_summary",
            #        "key": GOOGLE_API_KEY,
            #        "language": "fr"
            #    }
           # )
           # details_data = details_response.json()
            #description = details_data.get("result", {}).get("editorial_summary", {}).get("overview", "Description non disponible")

            description = attraction.get("editorial_summary", {}).get("overview", "Description non disponible")
            
            results.append({
                "name": name,
                "address": address,
                "place_id": place_id,
                "rating": rating,
                "photo_url": photo_url,
                "description": description,
                "website_uri": website_uri,
                "google_maps_uri": google_maps_uri
            })
        return results
    else:
        print("Aucun point d'intérêt trouvé ou une erreur est survenue.")
        return None

# Obtenir l'ID du lieu
coordinates_direct = get_city_coordinates(city_name)

# 2. Obtenir les coordonnées en deux étapes : d'abord l'ID du lieu, puis les coordonnées
place_id = get_place_id(city_name)
coordinates_from_place_id = get_coordinates_from_place_id(place_id) if place_id else None

# Affichage des résultats pour comparaison
print("Résultats avec get_city_coordinates :")
if coordinates_direct:
    print(f"Coordonnées de {city_name} : Latitude = {coordinates_direct[0]}, Longitude = {coordinates_direct[1]}")
else:
    print("Les coordonnées n'ont pas pu être obtenues avec get_city_coordinates.")

print("\nRésultats avec get_place_id et get_coordinates_from_place_id :")
if coordinates_from_place_id:
    print(f"Coordonnées de {city_name} : Latitude = {coordinates_from_place_id[0]}, Longitude = {coordinates_from_place_id[1]}")
else:
    print("Les coordonnées n'ont pas pu être obtenues avec get_place_id et get_coordinates_from_place_id.")



attractions = get_tourist_attractions_nearby(coordinates_from_place_id[0], coordinates_from_place_id[1])
if attractions:
    for i, attraction in enumerate(attractions, start=1):
        print(f"Attraction {i}:")
        print(f"Nom : {attraction['name']}")
        print(f"Adresse : {attraction['address']}")
        print(f"ID : {attraction['place_id']}")
        print(f"Note : {attraction['rating']}\n")
        print(f"Photo URL : {attraction['photo_url']}")
        print(f"Site web : {attraction['website_uri']}\n")
        print(f"Google Maps : {attraction['google_maps_uri']}\n")
        print(f"Description : {attraction['description']}\n")
else:
    print("Aucune attraction trouvée.")