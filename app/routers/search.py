from fastapi import APIRouter
from fastapi.responses import JSONResponse
from typing import Optional
from app.services.autocomplete_service import AutocompleteService
from app.core.exceptions import PlaceNotFoundError
from app.core.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter(prefix="/search", tags=["Search"])


@router.get("/autocomplete")
async def autocomplete(
    input: str,
    session_token: Optional[str] = None,
    language: str = "fr"
):
    logger.info(f"HTTP | GET /search/autocomplete — input={input} has_session={session_token is not None}")

    if len(input) < 4:
        logger.info(f"HTTP | GET /search/autocomplete — input trop court ({len(input)} chars)")
        return JSONResponse(content=[])

    service = AutocompleteService()
    predictions = await service.autocomplete(input, session_token, language)

    logger.info(f"HTTP | GET /search/autocomplete — {len(predictions)} résultats")
    return JSONResponse(content=predictions)


@router.get("/coordinates")
async def get_coordinates(
    place_id: str,
    session_token: Optional[str] = None
):
    logger.info(f"HTTP | GET /search/coordinates — place_id={place_id} has_session={session_token is not None}")

    service = AutocompleteService()
    coordinates = await service.get_coordinates(place_id, session_token)

    if not coordinates:
        raise PlaceNotFoundError(place_id)

    logger.info(f"HTTP | GET /search/coordinates — succès place_id={place_id}")
    return JSONResponse(content=coordinates)