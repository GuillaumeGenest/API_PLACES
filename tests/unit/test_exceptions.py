import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from http import HTTPStatus
from app.core.exceptions import (
    AppError,
    ErrorCode,
    PlaceNotFoundError,
    AttractionNotFoundError,
    ImageNotFoundError,
    PlaceIdMissingError,
    InvalidPlaceIdError,
    DescriptionNotFoundError,
    AIGenerationError,
    TripGenerationError,
)


class TestAppError(unittest.TestCase):

    def test_default_status_and_code(self):
        exc = AppError("erreur générique")
        self.assertEqual(exc.status_code, HTTPStatus.INTERNAL_SERVER_ERROR)
        self.assertEqual(exc.error_code, ErrorCode.INTERNAL_ERROR)
        self.assertEqual(exc.detail, "erreur générique")


class TestBusinessExceptions(unittest.TestCase):

    def test_place_not_found_error(self):
        exc = PlaceNotFoundError("Paris")
        self.assertEqual(exc.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(exc.error_code, ErrorCode.PLACE_NOT_FOUND)
        self.assertEqual(exc.detail, "Lieu introuvable : Paris")

    def test_attraction_not_found_error(self):
        exc = AttractionNotFoundError()
        self.assertEqual(exc.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(exc.error_code, ErrorCode.ATTRACTION_NOT_FOUND)

    def test_image_not_found_error(self):
        exc = ImageNotFoundError()
        self.assertEqual(exc.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(exc.error_code, ErrorCode.IMAGE_NOT_FOUND)

    def test_place_id_missing_error(self):
        exc = PlaceIdMissingError()
        self.assertEqual(exc.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(exc.error_code, ErrorCode.PLACE_ID_MISSING)

    def test_invalid_place_id_error(self):
        exc = InvalidPlaceIdError("../etc/passwd")
        self.assertEqual(exc.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(exc.error_code, ErrorCode.INVALID_PLACE_ID)
        self.assertEqual(exc.place_id, "../etc/passwd")

    def test_description_not_found_error(self):
        exc = DescriptionNotFoundError()
        self.assertEqual(exc.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(exc.error_code, ErrorCode.DESCRIPTION_NOT_FOUND)

    def test_ai_generation_error(self):
        exc = AIGenerationError("Tour Eiffel")
        self.assertEqual(exc.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(exc.error_code, ErrorCode.AI_GENERATION_ERROR)
        self.assertIn("Tour Eiffel", exc.detail)

    def test_trip_generation_error(self):
        exc = TripGenerationError()
        self.assertEqual(exc.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(exc.error_code, ErrorCode.TRIP_GENERATION_ERROR)

    def test_all_business_exceptions_are_app_errors(self):
        for exc_class in (
            PlaceNotFoundError, AttractionNotFoundError, ImageNotFoundError,
            PlaceIdMissingError, InvalidPlaceIdError, DescriptionNotFoundError,
            AIGenerationError, TripGenerationError,
        ):
            self.assertTrue(issubclass(exc_class, AppError))


if __name__ == '__main__':
    unittest.main(verbosity=2)
