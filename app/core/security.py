import os  # ← ajoute cet import en haut
import jwt
from jwt import PyJWKClient
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from app.core.config import get_supabase_url
from app.core.logger import setup_logger

logger = setup_logger(__name__)

PUBLIC_ROUTES = [
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/images/storage/caches",
]

jwks_client = PyJWKClient(f"{get_supabase_url()}/auth/v1/.well-known/jwks.json")

async def auth_middleware(request: Request, call_next):
    # ── Mode test — bypass total ──────────────────────────
    if os.getenv("TESTING") == "true":
        request.state.user = {
            "sub": "febfedf3-f6fc-4043-8dce-daf2d2b95906",
            "email": "test@test.com",
            "role": "authenticated"
        }
        return await call_next(request)
    # ─────────────────────────────────────────────────────

    if any(request.url.path.startswith(route) for route in PUBLIC_ROUTES):
        return await call_next(request)

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        logger.warning(f"🔒 Requête sans token → {request.url.path}")
        return JSONResponse(status_code=401, content={"detail": "Token manquant"})

    token = auth_header.replace("Bearer ", "")

    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256"],
            audience="authenticated"
        )
        request.state.user = payload
        logger.debug(f"✅ Token valide → user {payload.get('sub')}")

    except jwt.ExpiredSignatureError:
        logger.warning(f"🔒 Token expiré → {request.url.path}")
        return JSONResponse(status_code=401, content={"detail": "Token expiré"})
    except jwt.InvalidTokenError as e:
        logger.warning(f"🔒 Token invalide → {request.url.path} | {e}")
        return JSONResponse(status_code=401, content={"detail": "Token invalide"})
    except Exception as e:
        logger.error(f"🔒 Erreur auth → {e}")
        return JSONResponse(status_code=500, content={"detail": "Erreur authentification"})

    return await call_next(request)


def get_current_user(request: Request) -> dict:
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Non authentifié")
    return user