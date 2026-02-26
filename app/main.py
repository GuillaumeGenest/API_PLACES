from fastapi import FastAPI
from app.core.exceptions import add_exception_handlers
from app.routers import attractions, attraction, images, descriptions, ai, trips, countries_info

app = FastAPI(
    title="Places API",
    description="API de gestion des lieux touristiques",
    version="1.0.0"
)

add_exception_handlers(app)

app.include_router(attractions.router)
app.include_router(attraction.router)
app.include_router(images.router)
app.include_router(descriptions.router)
app.include_router(ai.router)
app.include_router(trips.router)
app.include_router(countries_info.router)