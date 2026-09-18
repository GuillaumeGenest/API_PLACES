from fastapi import APIRouter, Depends, Query
from typing import Optional
from app.services.ai_service import AIService
from app.core.exceptions import DescriptionNotFoundError
from app.core.logger import setup_logger
from app.core.security import get_current_user

logger = setup_logger(__name__)
router = APIRouter(prefix="/descriptions", tags=["Descriptions"])

@router.get("/")
async def get_description(
    place_name: str = Query(..., max_length=100),
    address: Optional[str] = Query(None, max_length=150),
    user: dict = Depends(get_current_user)
):
    logger.info(f"HTTP | GET /descriptions — place={place_name} address={address}")
    service = AIService()
    description = await service.generate_description(place_name, address, user_id=user["sub"])
    if not description:
        logger.error(f"HTTP | GET /descriptions — échec génération place={place_name}")
        raise DescriptionNotFoundError()
    logger.info(f"HTTP | GET /descriptions — succès place={place_name} longueur={len(description)} chars")
    return description