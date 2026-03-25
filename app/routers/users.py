from fastapi import APIRouter, Depends, HTTPException, Header, status
from app.supabase_service import _client
from app.supabase_admin import _admin_client
from app.services.supabase_service import get_user_from_token, delete_user
from app.core.logger import setup_logger
logger = setup_logger(__name__)

# 👉 on appelle directement "router"
router = APIRouter(prefix="/user", tags=["User"])

def get_token(authorization: str = Header(...)) -> str:
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Header Authorization invalide"
        )
    return authorization.replace("Bearer ", "")


@router.delete("/delete")
async def delete_me(token: str = Depends(get_token)):
    # 🔹 Vérifie le JWT et récupère l'user
    user = get_user_from_token(token)
    user_id = user.id

    # 🔹 Supprime via service_role
    success = delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Impossible de supprimer l'utilisateur"
        )

    return {"status": "success", "user_id": user_id}