from supabase import create_client, Client
from typing import Optional
from fastapi import HTTPException, status
from app.core.config import get_supabase_url, get_supabase_key
from app.core.logger import setup_logger
from datetime import datetime, timezone

logger = setup_logger(__name__)

# ─── Client Supabase — instancié une seule fois ───────────────────
_client: Client = create_client(get_supabase_url(), get_supabase_key())

# ─── MARK: - AUTH (AJOUT) ─────────────────────────────────────────

def get_user_from_token(token: str):
    try:
        user_response = _client.auth.get_user(token)

        if not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Utilisateur non authentifié"
            )

        return user_response.user

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"SUPABASE | Erreur get_user_from_token — error={e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide"
        )

# ─── MARK: - USER (AJOUT) ─────────────────────────────────────────

def delete_user(user_id: str) -> bool:
    try:
        logger.info(f"SUPABASE | Suppression user — id={user_id}")

        _client.auth.admin.delete_user(user_id)

        logger.info(f"SUPABASE | ✅ User supprimé — id={user_id}")
        return True

    except Exception as e:
        logger.error(f"SUPABASE | Erreur delete_user — id={user_id} error={e}")
        return False

# ─── MARK: - Check ────────────────────────────────────────────────

def get_attraction_by_place_id(place_id: str) -> Optional[dict]:
    try:
        logger.info(f"SUPABASE | Recherche attraction — place_id={place_id}")
        response = _client.table("Attraction").select("*").eq("place_id", place_id).execute()
        if response.data:
            logger.info(f"SUPABASE | ✅ Attraction trouvée — place_id={place_id}")
            return response.data[0]
        logger.info(f"SUPABASE | ❌ Attraction non trouvée — place_id={place_id}")
        return None
    except Exception as e:
        logger.error(f"SUPABASE | Erreur get_attraction_by_place_id — place_id={place_id} error={e}")
        return None

# ─── MARK: - Save ─────────────────────────────────────────────────

def save_attraction(attraction: dict) -> bool:
    try:
        place_id = attraction.get("place_id")
        logger.info(f"SUPABASE | Sauvegarde attraction — place_id={place_id}")

        rating = attraction.get("rating")
        if isinstance(rating, str):
            rating = None

        data = {
            "place_id": place_id,
            "name": attraction.get("name"),
            "address": attraction.get("address"),
            "latitude": attraction.get("latitude"),
            "longitude": attraction.get("longitude"),
            "rating": rating,
            "user_ratings_total": attraction.get("user_ratings_total"),
            "photo_urls": attraction.get("photo_urls", []),
            "website": attraction.get("website"),
            "google_maps_url": attraction.get("google_maps_url"),
            "phone": attraction.get("phone"),
            "description": attraction.get("description"),
            "opening_hours": attraction.get("opening_hours") or [],
            "price_level": attraction.get("price_level"),
            "price_range": attraction.get("price_range"),
            "category": attraction.get("category"),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        _client.table("Attraction").upsert(data, on_conflict="place_id").execute()
        logger.info(f"SUPABASE | ✅ Attraction sauvegardée — place_id={place_id}")
        return True

    except Exception as e:
        logger.error(f"SUPABASE | Erreur save_attraction — place_id={place_id} error={e}")
        return False

# ─── MARK: - Delete ───────────────────────────────────────────────

def delete_attraction(place_id: str) -> bool:
    try:
        logger.info(f"SUPABASE | Suppression attraction — place_id={place_id}")
        _client.table("Attraction").delete().eq("place_id", place_id).execute()
        logger.info(f"SUPABASE | ✅ Attraction supprimée — place_id={place_id}")
        return True
    except Exception as e:
        logger.error(f"SUPABASE | Erreur delete_attraction — place_id={place_id} error={e}")
        return False