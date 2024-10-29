from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import requests
import os
from typing import List, Optional
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

app = FastAPI(title="Tourist Places API")

# Récupérer la clé API de Google Places depuis les variables d'environnement
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise Exception("La clé API Google Places n'est pas configurée")




def get_place_info(address):
# Base URL
  base_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
# Parameters in a dictionary
  params = {
   "input": address,
   "inputtype": "textquery",
   "fields": "formatted_address,name,business_status,place_id",
   "key": GOOGLE_API_KEY,
  }
# Send request and capture response
  response = requests.get(base_url, params=params)
# Check if the request was successful
  if response.status_code == 200:
    return response.json()
  else:
    return None








class Location(BaseModel):
    name: str
    type: str = "city"  # "city" ou "country"

class TouristPlace(BaseModel):
    name: str
    address: str
    rating: Optional[float]
    types: List[str]
    photo_reference: Optional[str]
    place_id: str

class TouristResponse(BaseModel):
    location: str
    places: List[TouristPlace]

async def get_place_id(location: str) -> str:
    """Obtenir le place_id de Google pour une localisation donnée"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://maps.googleapis.com/maps/api/place/findplacefromtext/json",
            params={
                "input": location,
                "inputtype": "textquery",
                "key": GOOGLE_API_KEY,
            }
        )
        data = response.json()
        
        if data["status"] != "OK":
            raise HTTPException(status_code=404, detail="Location not found")
        
        return data["candidates"][0]["place_id"]

async def get_tourist_places(place_id: str) -> List[dict]:
    """Obtenir les lieux touristiques autour d'un place_id"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://maps.googleapis.com/maps/api/place/nearbysearch/json",
            params={
                "location": await get_location_coordinates(place_id),
                "radius": "5000",  # Rayon de 5km
                "type": "tourist_attraction",
                "key": GOOGLE_API_KEY,
                "language": "fr"  # Résultats en français
            }
        )
        return response.json()["results"]

async def get_location_coordinates(place_id: str) -> str:
    """Obtenir les coordonnées géographiques d'un place_id"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://maps.googleapis.com/maps/api/place/details/json",
            params={
                "place_id": place_id,
                "fields": "geometry",
                "key": GOOGLE_API_KEY,
            }
        )
        data = response.json()
        lat = data["result"]["geometry"]["location"]["lat"]
        lng = data["result"]["geometry"]["location"]["lng"]
        return f"{lat},{lng}"

@app.post("/tourist-places/", response_model=TouristResponse)
async def find_tourist_places(location: Location):
    """
    Endpoint principal pour obtenir les lieux touristiques
    Accepte un nom de ville ou de pays et retourne les attractions touristiques
    """
    try:
        # Obtenir le place_id de la localisation
        place_id = await get_place_id(location.name)
        
        # Obtenir les lieux touristiques
        places_data = await get_tourist_places(place_id)
        
        # Formater les résultats
        tourist_places = []
        for place in places_data:
            tourist_place = TouristPlace(
                name=place["name"],
                address=place.get("vicinity", "Adresse non disponible"),
                rating=place.get("rating"),
                types=place.get("types", []),
                photo_reference=place.get("photos", [{}])[0].get("photo_reference") if "photos" in place else None,
                place_id=place["place_id"]
            )
            tourist_places.append(tourist_place)
        
        return TouristResponse(
            location=location.name,
            places=tourist_places
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Endpoint de vérification de santé de l'API"""
    return {"status": "healthy"}