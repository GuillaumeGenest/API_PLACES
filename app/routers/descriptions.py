from fastapi import APIRouter
from typing import Optional
from app.services.ai_service import AIService
from app.core.exceptions import DescriptionNotFoundError

router = APIRouter(prefix="/descriptions", tags=["Descriptions"])

# /descriptions/  →  ancien /generate_description
@router.get("/")
def get_description(place_name: str, address: Optional[str] = None):
    service = AIService()
    description = service.generate_description(place_name, address)
    if not description:
        raise DescriptionNotFoundError()
    return description