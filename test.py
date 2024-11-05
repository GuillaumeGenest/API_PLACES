import requests
import os
import json

from API_Places import *

city_name = 'Rome'


def display_attractions(attractions):
    """
    Affiche les attractions de manière formatée
    """
    if attractions:
        for i, attraction in enumerate(attractions, start=1):
            print("\n" + "="*50)
            print(f"Attraction {i}:")
            print(f"Nom : {attraction['name']}")
            print(f"Adresse : {attraction['address']}")
            print(f"ID : {attraction['place_id']}")
            print(f"Note : {attraction['rating']}")
            for photo_url in attraction["photo_urls"]:
                print(photo_url)
            print(f"Site web : {attraction['website']}")
            print(f"Google Maps : {attraction['google_maps_url']}")
            print(f"Téléphone : {attraction['phone']}")
            print(f"Nombre d'avis : {attraction['user_ratings_total']}")
            print(f"Description : {attraction['description']}\n")
            print("HEURES D'OUVERTURE :")
            if attraction['opening_hours']:
                for hour in attraction['opening_hours']:
                    print(hour)
            else:
                print("Horaires non disponibles")
    else:
        print("Aucune attraction trouvée.")

coordinates_direct = get_city_coordinates(city_name)

# 2. Obtenir les coordonnées en deux étapes : d'abord l'ID du lieu, puis les coordonnées

# Affichage des résultats pour comparaison
print("Résultats avec get_city_coordinates :")
if coordinates_direct:
    print(f"Coordonnées de {city_name} : Latitude = {coordinates_direct[0]}, Longitude = {coordinates_direct[1]}")
else:
    print("Les coordonnées n'ont pas pu être obtenues avec get_city_coordinates.")

resultats = get_tourist_attractions_nearby(coordinates_direct[0], coordinates_direct[1])
display_attractions(resultats)