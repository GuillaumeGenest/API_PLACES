from enum import Enum
from http import HTTPStatus
from fastapi import Request
from fastapi.responses import JSONResponse


# ─── Codes d'erreur ───────────────────────────────────────────────────────────

class ErrorCode(str, Enum):
    INTERNAL_ERROR = "INTERNAL_ERROR"
    PLACE_NOT_FOUND = "PLACE_NOT_FOUND"
    ATTRACTION_NOT_FOUND = "ATTRACTION_NOT_FOUND"
    IMAGE_NOT_FOUND = "IMAGE_NOT_FOUND"
    PLACE_ID_MISSING = "PLACE_ID_MISSING"
    INVALID_PLACE_ID = "INVALID_PLACE_ID"
    DESCRIPTION_NOT_FOUND = "DESCRIPTION_NOT_FOUND"
    AI_GENERATION_ERROR = "AI_GENERATION_ERROR"
    TRIP_GENERATION_ERROR = "TRIP_GENERATION_ERROR"


# ─── Exceptions custom ────────────────────────────────────────────────────────

class AppError(Exception):
    status_code: HTTPStatus = HTTPStatus.INTERNAL_SERVER_ERROR
    error_code: ErrorCode = ErrorCode.INTERNAL_ERROR

    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)


class PlaceNotFoundError(AppError):
    status_code = HTTPStatus.BAD_REQUEST
    error_code = ErrorCode.PLACE_NOT_FOUND

    def __init__(self, place_name: str):
        self.place_name = place_name
        super().__init__(f"Lieu introuvable : {place_name}")


class AttractionNotFoundError(AppError):
    status_code = HTTPStatus.NOT_FOUND
    error_code = ErrorCode.ATTRACTION_NOT_FOUND

    def __init__(self):
        super().__init__("Aucune attraction trouvée")


class ImageNotFoundError(AppError):
    status_code = HTTPStatus.NOT_FOUND
    error_code = ErrorCode.IMAGE_NOT_FOUND

    def __init__(self):
        super().__init__("Aucun url trouvé")


class PlaceIdMissingError(AppError):
    status_code = HTTPStatus.BAD_REQUEST
    error_code = ErrorCode.PLACE_ID_MISSING

    def __init__(self):
        super().__init__("place_id manquant")


class InvalidPlaceIdError(AppError):
    status_code = HTTPStatus.BAD_REQUEST
    error_code = ErrorCode.INVALID_PLACE_ID

    def __init__(self, place_id: str):
        self.place_id = place_id
        super().__init__("place_id invalide")


class DescriptionNotFoundError(AppError):
    status_code = HTTPStatus.NOT_FOUND
    error_code = ErrorCode.DESCRIPTION_NOT_FOUND

    def __init__(self):
        super().__init__("Impossible de générer une description pour ce lieu")


class AIGenerationError(AppError):
    status_code = HTTPStatus.BAD_REQUEST
    error_code = ErrorCode.AI_GENERATION_ERROR

    def __init__(self, place_name: str):
        self.place_name = place_name
        super().__init__(f"Erreur lors de la génération IA pour le lieu {place_name}")


class TripGenerationError(AppError):
    status_code = HTTPStatus.BAD_REQUEST
    error_code = ErrorCode.TRIP_GENERATION_ERROR

    def __init__(self):
        super().__init__("Erreur dans les informations sur la requête")


# ─── Handler global ───────────────────────────────────────────────────────────

def add_exception_handlers(app):

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.error_code.value,
                "detail": exc.detail
            }
        )
