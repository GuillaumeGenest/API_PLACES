from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from API_Places import *

app = FastAPI()

@app.get("/attractions/{city_name}")
def get_attractions(city_name):
    coordinates = get_city_coordinates(city_name)
    if coordinates:
        attractions = get_tourist_attractions_nearby(coordinates[0], coordinates[1])
        if attractions:
            return JSONResponse(content={"attractions": attractions})
        else:
            raise HTTPException(status_code=404, detail="Aucune attraction trouvée")
    else:
        raise HTTPException(status_code=400, detail=f"Erreur dans les coordonnées de la ville {city_name}, cette dernière n'existe pas")
    

@app.get("/attractions_with_coordinates/{latitude}-{longitude}")
def get_attractions_by_coordinates(latitude: float, longitude: float):
    attractions = get_tourist_attractions_nearby(latitude, longitude)
    if attractions:
        return JSONResponse(content={"attractions": attractions})
    else:
        raise HTTPException(status_code=404, detail="Aucune attraction trouvée")

@app.get("/attraction/{place_name}")
def get_attraction_information(place_name):
    place_id = get_place_id(place_name)
    if place_id:
        attraction = get_tourist_attraction(place_id)
        if attraction:
            return JSONResponse(content={"attractions": attraction})
        else:
            raise HTTPException(status_code=404, detail="Aucune attraction trouvée")
    else:
        raise HTTPException(status_code=400, detail=f"Erreur dans les coordonnées de la ville {place_name}, cette dernière n'existe pas")

@app.get("/attraction_with_coordinates/{latitude}-{longitude}")
def get_attraction_information_by_coordinates(latitude: float, longitude: float):
    place_id = get_place_id_from_coordinates(latitude, longitude)
    print(f"valeur de place_id {place_id}")
    if place_id:
        attraction = get_tourist_attraction(place_id)
        if attraction:
            return JSONResponse(content={"attractions": attraction})
        else:
            raise HTTPException(status_code=404, detail="Aucune attraction trouvée")
    else:
        raise HTTPException(status_code=400, detail=f"Erreur dans les coordonnées de la ville {latitude} - {longitude}, cette dernière n'existe pas")