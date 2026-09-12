from fastapi import APIRouter
from app.services.places_service import PlacesService
from app.models.attraction import AttractionCategory, AttractionResponse
from app.core.exceptions import PlaceNotFoundError, AttractionNotFoundError
from app.core.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter(prefix="/attractions", tags=["Attractions"])


@router.get("/", response_model=AttractionResponse)
async def get_attractions(city_name: str, category: AttractionCategory):
    logger.info(f"HTTP | GET /attractions — city={city_name} category={category.value}")
    service = PlacesService()
    coordinates = await service.get_city_coordinates(city_name)
    if not coordinates:
        logger.warning(f"HTTP | GET /attractions — ville introuvable city={city_name}")
        raise PlaceNotFoundError(city_name)
    attractions = await service.get_tourist_attractions_nearby(
        coordinates[0], coordinates[1], category
    )
    if not attractions:
        logger.error(f"HTTP | GET /attractions — aucune attraction city={city_name} category={category.value}")
        raise AttractionNotFoundError()
    logger.info(f"HTTP | GET /attractions — succès city={city_name} category={category.value}")
    return attractions


@router.get("/by_coordinates", response_model=AttractionResponse)
async def get_attractions_by_coordinates(
    latitude: float,
    longitude: float,
    category: AttractionCategory
):
    logger.info(f"HTTP | GET /attractions/by_coordinates — lat={latitude} lng={longitude} category={category.value}")
    service = PlacesService()
    attractions = await service.get_tourist_attractions_nearby(latitude, longitude, category)
    if not attractions:
        logger.error(f"HTTP | GET /attractions/by_coordinates — aucune attraction lat={latitude} lng={longitude}")
        raise AttractionNotFoundError()
    logger.info(f"HTTP | GET /attractions/by_coordinates — succès lat={latitude} lng={longitude} category={category.value}")
    return attractions