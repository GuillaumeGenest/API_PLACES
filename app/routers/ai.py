from fastapi import APIRouter, Depends, Query
from typing import Optional
from app.services.ai_service import AIService
from app.core.exceptions import AIGenerationError
from app.core.logger import setup_logger
from app.core.security import get_current_user
from app.models.attraction import AttractionResponse

logger = setup_logger(__name__)
router = APIRouter(prefix="/ai", tags=["AI"])

@router.get("/attraction", response_model=AttractionResponse)
async def get_ai_attraction(
    place_name: str = Query(..., max_length=100),
    address: Optional[str] = Query(None, max_length=150),
    category: str = "autre",
    user: dict = Depends(get_current_user)
):
    logger.info(f"HTTP | GET /ai/attraction — place={place_name} address={address} category={category}")
    service = AIService()
    data = await service.generate_attraction(place_name, address, category, user_id=user["sub"])
    if not data:
        logger.error(f"HTTP | GET /ai/attraction — échec génération place={place_name}")
        raise AIGenerationError(place_name)
    logger.info(f"HTTP | GET /ai/attraction — succès place={place_name}")
    return data