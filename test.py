import requests
import os
import json


# Récupérer la clé API de Google Places depuis les variables d'environnement
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise Exception("La clé API Google Places n'est pas configurée")

city_name = 'Venise'



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
            "rankPreference": "POPULARITY",
            "type": "tourist_attraction",
            "key": GOOGLE_API_KEY,
            "language": "fr"  # Résultats en français
        }
    )
    data = response.json()
    
    if data['status'] == 'OK':
        attractions = data['results'][:20]
        #print(json.dumps(data, indent=2))
        results = []
        for attraction in attractions:
            # Extraction des informations principales
            name = attraction.get("name", "Nom non disponible")
            address = attraction.get("vicinity", "Adresse non disponible")
            place_id = attraction.get("place_id", "ID non disponible")
            rating = attraction.get("rating", "Note non disponible")
            user_ratings_total = attraction.get("user_ratings_total", 0)
            website = attraction.get("websiteUri", "Site web non disponible")
            phone = attraction.get("formatted_phone_number", "Téléphone non disponible")
            google_maps_url = attraction.get("googleMapsUri", "Lien Google Maps non disponible")



            # Récupération de la photo si disponible
            photo_url = None
            if "photos" in attraction:
                photo_reference = attraction["photos"][0]["photo_reference"]
                photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_reference}&key={GOOGLE_API_KEY}"
            
            results.append({
                "name": name,
                "address": address,
                "place_id": place_id,
                "rating": rating,
                "photo_url": photo_url,
                "website": website,
                "google_maps_url": google_maps_url,
                "phone": phone,
                "user_ratings_total": user_ratings_total
            })
        return results
    else:
        print("Aucun point d'intérêt trouvé ou une erreur est survenue.")
        return None





def get_place_details(place_id):
    """
    Récupère les détails d'un lieu à partir de son ID Google Place.
    
    Paramètres :
    place_id (str) : L'ID unique du lieu sur Google Place.
    api_key (str) : Votre clé d'API Google.
    
    Retourne :
    dict : Un dictionnaire contenant les informations du lieu, ou None en cas d'erreur.
    """
    # Endpoint de l'API Google Place Details
    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key={GOOGLE_API_KEY}&language=fr"
    
    try:
        # Faites la requête à l'API
        response = requests.get(url)
        
        # Vérifiez que la requête a réussi
        if response.status_code == 200:
            # Récupérez les données du lieu
            data = response.json()["result"]
            
            
            
            # Extrayez les informations dont vous avez besoin
            place_info = {
                "name": data.get("name"),
                "address": data.get("formatted_address"),
                "phone": data.get("formatted_phone_number"),
                "website": data.get("website"),
                "opening_hours": data["opening_hours"]["weekday_text"] if "opening_hours" in data else None,
                "description": data.get("editorial_summary", {}).get("overview", "Aucune description disponible"),
                # Construire l'URL de chaque photo
                 "photos": [
                     f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photo_reference={photo_data['photo_reference']}&key={GOOGLE_API_KEY}"
                for photo_data in data["photos"]
                ] if "photos" in data else []
            }
            
            return place_info
        else:
            print(f"Erreur lors de la récupération des informations du lieu : {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête à l'API : {e}")
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
        print("\n" + "="*50)
        print(f"Attraction {i}:")
        print(f"Nom : {attraction['name']}")
        print(f"Adresse : {attraction['address']}")
        print(f"ID : {attraction['place_id']}")
        print(f"Note : {attraction['rating']}\n")
        print(f"Photo URL : {attraction['photo_url']}")
        print(f"Site web : {attraction['website']}")
        print(f"Google Maps : {attraction['google_maps_url']}")
        print(f"Phone : {attraction['phone']}")
        print(f"user_ratings_total : {attraction['user_ratings_total']}")
       #print(f"Description : {attraction['description']}\n")
else:
    print("Aucune attraction trouvée.")


place_id = "ChIJv2xSZNexfkcRBaKsgyfVEgo"


print("\n" + "="*50)
print("\n" + "="*50)
print("\n" + "="*50)
place_details = get_place_details(place_id)
if place_details:
    print(f"Nom : {place_details['name']}")
    print(f"Adresse : {place_details['address']}")
    print(f"Téléphone : {place_details['phone']}")
    print(f"Site web : {place_details['website']}")
    print(f"Description : {place_details['description']}")
    print(f"Heures d'ouverture :")
    print("HEURES D'OUVERTURE :")
    if place_details['opening_hours']:
        for hour in place_details['opening_hours']:
            print(hour)
    else:
        print("Horaires non disponibles")
    print("URLs des photos :")
    for photo_url in place_details["photos"]:
        print(photo_url)

        """
        Rajouter filtre et filtrer en fonction du user_ratings_total 
        Mettre sous forme de fonction 
        Placer cela comme une API 
        """