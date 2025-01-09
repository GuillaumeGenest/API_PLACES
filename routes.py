from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from API_Places import *

app = FastAPI()

#"""
#    Requête pour Récupèrer et retourner les lieux avec leurs informations à partir d'un espace dont le centre est données par un nom
#
#"""

@app.get("/attractions/city={city_name}&category={category}")
def get_attractions(city_name, category: AttractionCategory):
    coordinates = get_city_coordinates(city_name)
    if coordinates:
        attractions = get_tourist_attractions_nearby(coordinates[0], coordinates[1], category)
        if attractions:
            return JSONResponse(content=attractions)
        else:
            raise HTTPException(status_code=404, detail="Aucune attraction trouvée")
    else:
        raise HTTPException(status_code=400, detail=f"Erreur dans les coordonnées de la ville {city_name}, cette dernière n'existe pas")
    
#"""
#    Requête pour Récupèrer et retourner les lieux avec leurs informations à partir d'un espace dont le centre correspond aux coordonnées
#
#"""

@app.get("/attractions_with_coordinates/coordinates={latitude}-{longitude}&attractions={attraction}")
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

@app.get("/attraction/{place_name}")
def get_attraction_information(place_name):
    place_id = get_place_id(place_name)
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

@app.get("/attraction_with_coordinates/{latitude}-{longitude}")
def get_attraction_information_by_coordinates(latitude: float, longitude: float):
    place_id = get_place_id_from_coordinates(latitude, longitude)
    print(f"valeur de place_id {place_id}")
    if place_id:
        attraction = get_tourist_attraction(place_id)
        if attraction:
            return JSONResponse(content= attraction)
        else:
            raise HTTPException(status_code=404, detail="Aucune attraction trouvée")
    else:
        raise HTTPException(status_code=400, detail=f"Erreur dans les coordonnées de la ville {latitude} - {longitude}, cette dernière n'existe pas")