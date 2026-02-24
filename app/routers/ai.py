from fastapi import APIRouter
from fastapi.responses import JSONResponse
from typing import Optional
from app.services.ai_service import AIService
from app.core.exceptions import AIGenerationError

router = APIRouter(prefix="/ai", tags=["AI"])

# /ai/attraction  →  ancien /generate_attraction
@router.get("/attraction")
def get_ai_attraction(
    place_name: str,
    address: Optional[str] = None,
    category: str = "autre"
):
    service = AIService()
    data = service.generate_attraction(place_name, address, category)
    if not data:
        raise AIGenerationError(place_name)
    return JSONResponse(content=data)