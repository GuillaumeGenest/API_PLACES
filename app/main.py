from fastapi import FastAPI
from app.core.logger import setup_logger
from app.core.exceptions import add_exception_handlers
from app.routers import attractions, attraction, images, descriptions, ai, trips, countries_info
from fastapi import FastAPI, Request
import time
logger = setup_logger("api")

app = FastAPI(
    title="Places API",
    description="API de gestion des lieux touristiques",
    version="1.0.0"
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    logger.info(f"→ {request.method} {request.url.path}")
    response = await call_next(request)
    duration = round((time.time() - start) * 1000, 2)
    logger.info(f"← {request.method} {request.url.path} | {response.status_code} | {duration}ms")
    return response

add_exception_handlers(app)

app.include_router(attractions.router)
app.include_router(attraction.router)
app.include_router(images.router)
app.include_router(descriptions.router)
app.include_router(ai.router)
app.include_router(trips.router)
app.include_router(countries_info.router)