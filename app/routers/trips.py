from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse
from typing import Optional
from app.services.photos_service import PhotosService
from app.services.places_service import PlacesService
from app.services.trip_service import generate_road_trip, generate_city_trip
from app.core.exceptions import PlaceNotFoundError, ImageNotFoundError, PlaceIdMissingError
from app.core.logger import setup_logger
from datetime import date
logger = setup_logger(__name__)


router = APIRouter(prefix="/trips", tags=["Trips"])

@router.get("/city")
def get_trip_in_city(city_name: str, firstdate: date, lastdate: date):
    logger.info(f"HTTP | GET /trips/city — city={city_name} from={firstdate} to={lastdate}")
    if firstdate > lastdate:
        logger.warning(f"HTTP | Dates invalides — from={firstdate} to={lastdate}")
        raise HTTPException(status_code=400, detail="La date de début doit être avant la date de fin")
    data = generate_city_trip(city_name, str(firstdate), str(lastdate))
    if data:
        logger.info(f"HTTP | GET /trips/city — succès city={city_name}")
        return JSONResponse(content=data)
    logger.error(f"HTTP | GET /trips/city — échec city={city_name}")
    raise HTTPException(status_code=400, detail="Erreur lors de la génération du trip")

@router.get("/roadtrip")
def get_roadtrip(region: str, firstdate: date, lastdate: date):
    logger.info(f"HTTP | GET /trips/roadtrip — region={region} from={firstdate} to={lastdate}")
    if firstdate > lastdate:
        logger.warning(f"HTTP | Dates invalides — from={firstdate} to={lastdate}")
        raise HTTPException(status_code=400, detail="La date de début doit être avant la date de fin")
    data = generate_road_trip(region, str(firstdate), str(lastdate))
    if data:
        logger.info(f"HTTP | GET /trips/roadtrip — succès region={region}")
        return JSONResponse(content=data)
    logger.error(f"HTTP | GET /trips/roadtrip — échec region={region}")
    raise HTTPException(status_code=400, detail="Erreur lors de la génération du road trip")