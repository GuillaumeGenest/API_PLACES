from fastapi import Request
from fastapi.responses import JSONResponse


# ─── Exceptions custom ────────────────────────────────────────────────────────

class PlaceNotFoundError(Exception):
    def __init__(self, place_name: str):
        self.place_name = place_name

class AttractionNotFoundError(Exception):
    pass

class ImageNotFoundError(Exception):
    pass

class PlaceIdMissingError(Exception):
    pass

class InvalidPlaceIdError(Exception):
    def __init__(self, place_id: str):
        self.place_id = place_id

class DescriptionNotFoundError(Exception):
    pass

class AIGenerationError(Exception):
    def __init__(self, place_name: str):
        self.place_name = place_name

class TripGenerationError(Exception):
    pass


# ─── Handlers globaux ─────────────────────────────────────────────────────────

def add_exception_handlers(app):

    @app.exception_handler(PlaceNotFoundError)
    async def place_not_found_handler(request: Request, exc: PlaceNotFoundError):
        return JSONResponse(
            status_code=400,
            content={
                "error": "PLACE_NOT_FOUND",
                "detail": f"Lieu introuvable : {exc.place_name}"
            }
        )

    @app.exception_handler(AttractionNotFoundError)
    async def attraction_not_found_handler(request: Request, exc: AttractionNotFoundError):
        return JSONResponse(
            status_code=404,
            content={
                "error": "ATTRACTION_NOT_FOUND",
                "detail": "Aucune attraction trouvée"
            }
        )

    @app.exception_handler(ImageNotFoundError)
    async def image_not_found_handler(request: Request, exc: ImageNotFoundError):
        return JSONResponse(
            status_code=404,
            content={
                "error": "IMAGE_NOT_FOUND",
                "detail": "Aucun url trouvé"
            }
        )

    @app.exception_handler(PlaceIdMissingError)
    async def place_id_missing_handler(request: Request, exc: PlaceIdMissingError):
        return JSONResponse(
            status_code=400,
            content={
                "error": "PLACE_ID_MISSING",
                "detail": "place_id manquant"
            }
        )

    @app.exception_handler(InvalidPlaceIdError)
    async def invalid_place_id_handler(request: Request, exc: InvalidPlaceIdError):
        return JSONResponse(
            status_code=400,
            content={
                "error": "INVALID_PLACE_ID",
                "detail": "place_id invalide"
            }
        )

    @app.exception_handler(DescriptionNotFoundError)
    async def description_not_found_handler(request: Request, exc: DescriptionNotFoundError):
        return JSONResponse(
            status_code=404,
            content={
                "error": "DESCRIPTION_NOT_FOUND",
                "detail": "Impossible de générer une description pour ce lieu"
            }
        )

    @app.exception_handler(AIGenerationError)
    async def ai_generation_error_handler(request: Request, exc: AIGenerationError):
        return JSONResponse(
            status_code=400,
            content={
                "error": "AI_GENERATION_ERROR",
                "detail": f"Erreur lors de la génération IA pour le lieu {exc.place_name}"
            }
        )

    @app.exception_handler(TripGenerationError)
    async def trip_generation_error_handler(request: Request, exc: TripGenerationError):
        return JSONResponse(
            status_code=400,
            content={
                "error": "TRIP_GENERATION_ERROR",
                "detail": "Erreur dans les informations sur la requête"
            }
        )