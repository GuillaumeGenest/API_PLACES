from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_current_user
from app.services.supabase_service import delete_user
from app.core.logger import setup_logger
logger = setup_logger(__name__)

router = APIRouter(prefix="/user", tags=["User"])


@router.delete("/delete")
async def delete_me(user: dict = Depends(get_current_user)):
    user_id = user["sub"]

    success = delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Impossible de supprimer l'utilisateur"
        )

    return {"status": "success", "user_id": user_id}
