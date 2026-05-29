from app.core.config import check_env
check_env()  # ← EN PREMIER avant tout autre import

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from app.core.logger import setup_logger
from app.core.exceptions import add_exception_handlers
from app.routers import attractions, attraction, images, descriptions, ai, trips, countries_info, users
from app.core.security import auth_middleware
import time
import os

logger = setup_logger("api")

# ─── Application ──────────────────────────────────────────────────
app = FastAPI(
    title="Places API",
    description="API de gestion des lieux touristiques",
    version="1.0.0"
)

# ─── Middleware ───────────────────────────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    logger.info(f"→ {request.method} {request.url.path}")
    response = await call_next(request)
    duration = round((time.time() - start) * 1000, 2)
    logger.info(f"← {request.method} {request.url.path} | {response.status_code} | {duration}ms")
    return response


app.middleware("http")(auth_middleware)

# ─── Exceptions ───────────────────────────────────────────────────
add_exception_handlers(app)

# ─── Static files ─────────────────────────────────────────────────
STORAGE_DIR = os.path.join(os.path.dirname(__file__), "..", "images", "storage", "caches")
os.makedirs(STORAGE_DIR, exist_ok=True)
app.mount("/images/storage/caches", StaticFiles(directory=STORAGE_DIR), name="storage")

# ─── Routers ──────────────────────────────────────────────────────
app.include_router(attractions.router)
app.include_router(attraction.router)
app.include_router(images.router)
app.include_router(descriptions.router)
app.include_router(ai.router)
app.include_router(trips.router)
app.include_router(countries_info.router)
app.include_router(users.router)