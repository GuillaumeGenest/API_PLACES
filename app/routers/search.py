from fastapi import APIRouter
from fastapi.responses import JSONResponse
from typing import Optional
from app.services.autocomplete_service import AutocompleteService
from app.core.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter(prefix="/search", tags=["Search"])


@router.get("/autocomplete")
async def autocomplete(
    input: str,
    session_token: Optional[str] = None,
    language: str = "fr"
):
    """
    Retourne une liste de suggestions de lieux.
    - input        : texte saisi (min 4 caractères)
    - session_token: UUID généré par Android (optionnel)
    - language     : langue des résultats (défaut: fr)
    """
    logger.info(f"HTTP | GET /search/autocomplete — input={input} has_session={session_token is not None}")

    if len(input) < 4:
        logger.info(f"HTTP | GET /search/autocomplete — input trop court ({len(input)} chars)")
        return JSONResponse(content=[])

    service = AutocompleteService()
    predictions = await service.autocomplete(input, session_token, language)

    logger.info(f"HTTP | GET /search/autocomplete — {len(predictions)} résultats")
    return JSONResponse(content=predictions)