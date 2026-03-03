from fastapi import APIRouter
from typing import Optional
from app.services.ai_service import AIService
from app.core.exceptions import DescriptionNotFoundError
from app.core.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/descriptions", tags=["Descriptions"])

@router.get("/")
def get_description(place_name: str, address: Optional[str] = None):
    logger.info(f"HTTP | GET /descriptions — place={place_name} address={address}")
    service = AIService()

    description = service.generate_description(place_name, address)
    if not description:
        logger.error(f"HTTP | GET /descriptions — échec génération place={place_name}")
        raise DescriptionNotFoundError()
    logger.info(f"HTTP | GET /descriptions — succès place={place_name} longueur={len(description)} chars")
    return description