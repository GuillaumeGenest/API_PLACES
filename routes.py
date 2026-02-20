from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from API_Places import *
from API_Trip import *
from typing import Optional
import urllib.parse
app = FastAPI()

#"""
#    Requête pour Récupèrer et retourner les lieux avec leurs informations à partir d'un espace dont le centre est données par un nom
#
#"""

@app.get("/attractions")
def get_attractions(city_name: str, category: AttractionCategory):
    print(f"city_name reçu : {city_name}")
    coordinates = get_city_coordinates(city_name)
    if coordinates:
        attractions = get_tourist_attractions_nearby(coordinates[0], coordinates[1], category)
        if attractions:
            return JSONResponse(content=attractions)
        else:
            raise HTTPException(status_code=404, detail="Aucune attraction trouvée")
    else:
        print(f"Lancement HTTPException pour ville inconnue {city_name}")
        raise HTTPException(
            status_code=400, 
            detail=f"Erreur dans les coordonnées de la ville {city_name}, cette dernière n'existe pas"
        )
#"""
#    Requête pour Récupèrer et retourner les lieux avec leurs informations à partir d'un espace dont le centre correspond aux coordonnées
#
#"""

@app.get("/attractions_with_coordinates")
def get_attractions_by_coordinates(latitude: float, longitude: float, attraction: AttractionCategory):
    attractions = get_tourist_attractions_nearby(latitude, longitude, attraction)
    if attractions:
        return JSONResponse(content=attractions)
    else:
        raise HTTPException(status_code=404, detail="Aucune attraction trouvée")
    
#"""
#    Requête pour Récupèrer et retourner le lieu et ses informations à partir du nom
#
#"""

@app.get("/attraction")
def get_attraction_information(place_name: str, address: str):
    decoded_name = urllib.parse.unquote(place_name)
    decoded_address = urllib.parse.unquote(address)
    place_id = get_place_id(decoded_name, decoded_address)
    if place_id:
        attraction = get_tourist_attraction(place_id)
        if attraction:
            return JSONResponse(content=attraction)
        else:
            raise HTTPException(status_code=404, detail="Aucune attraction trouvée")
    else:
        raise HTTPException(status_code=400, detail=f"Erreur dans les coordonnées de la ville {place_name}, cette dernière n'existe pas")

#"""
#    Requête pour Récupèrer et retourner le lieu et ses informations à partir des coordonnées
#
#"""

@app.get("/attraction_with_coordinates")
def get_attraction_information_by_coordinates(latitude: float, longitude: float):
    place_id = get_place_id_from_coordinates(latitude, longitude)
    print(f"valeur de place_id {place_id}")
    if place_id:
        attraction = get_tourist_attraction(place_id)
        if attraction:
            return JSONResponse(content=attraction)
        else:
            raise HTTPException(status_code=404, detail="Aucune attraction trouvée")
    else:
        raise HTTPException(status_code=400, detail=f"Erreur dans les coordonnées de la ville {latitude} - {longitude}, cette dernière n'existe pas")


###########################################################################################

###########################################################################################
@app.get("/generate_trip_city")
def get_trip_in_city(city_name: str, firstdate: str, lastdate: str):
    data = generate_city_trip(city_name, firstdate, lastdate)
    print(f"valeur de {data}")
    if data:
        return JSONResponse(content=data)
    else:
        raise HTTPException(status_code=400, detail=f"Erreur dans les informations sur la requete")

@app.get("/generate_road_trip")
def get_roadtrip(region: str, firstdate: str, lastdate: str):
    data = generate_road_trip(region, firstdate, lastdate)
    print(f"valeur de {data}")
    if data:
        return JSONResponse(content=data)
    else:
        raise HTTPException(status_code=400, detail="Erreur dans les informations sur la requête")

@app.get("/generate_url_image")
def get_url_photo(place: str):
    decoded_name = urllib.parse.unquote(place)
    place_id = get_place_id(decoded_name)
    print(f"valeur de place_id {place_id}")
    if place_id:
        url = get_url_image(place_id)
        if url:
            return JSONResponse(content=url)
        else:
            raise HTTPException(status_code=404, detail="Aucun url trouvé")
    else:
        raise HTTPException(status_code=400, detail=f"Erreur dans le nom de la ville/région {place}, cette dernière n'existe pas")


@app.get("/generate_ai_attraction")
def get_ai_attraction(place_name: str, address: Optional[str] = None, category: str = "autre"):
    decoded_name = urllib.parse.unquote(place_name)
    decoded_address = urllib.parse.unquote(address) if address else None
    data = generate_ai_attraction(decoded_name, decoded_address, category)
    print(f"valeur de {data}")
    if data:
        return JSONResponse(content=data)
    else:
        raise HTTPException(status_code=400, detail=f"Erreur lors de la génération IA pour le lieu {place_name}")