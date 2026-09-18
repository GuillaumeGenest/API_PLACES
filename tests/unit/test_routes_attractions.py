import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app


class TestGetAttractions(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_get_attractions_success(self):
        with patch('app.routers.attractions.PlacesService') as MockService:
            instance = MockService.return_value
            instance.get_city_coordinates = AsyncMock(return_value=(48.8566, 2.3522))
            instance.get_tourist_attractions_nearby = AsyncMock(return_value={
                "attraction": [{"name": "Tour Eiffel", "address": "Paris", "place_id": "ChIJD7fiBh9u5kcRYJSMaMOCCwQ"}]
            })
            response = self.client.get("/attractions/?city_name=Paris&category=touristique")
            self.assertEqual(response.status_code, 200)
            self.assertIn("attraction", response.json())

    def test_get_attractions_city_not_found(self):
        with patch('app.routers.attractions.PlacesService') as MockService:
            instance = MockService.return_value
            instance.get_city_coordinates = AsyncMock(return_value=None)
            response = self.client.get("/attractions/?city_name=Inconnu&category=touristique")
            self.assertEqual(response.status_code, 404)
            self.assertIn("PLACE_NOT_FOUND", response.json()["error"])

    def test_get_attractions_by_coordinates_success(self):
        with patch('app.routers.attractions.PlacesService') as MockService:
            instance = MockService.return_value
            instance.get_tourist_attractions_nearby = AsyncMock(return_value={
                "attraction": [{"name": "Tour Eiffel", "address": "Paris", "place_id": "ChIJD7fiBh9u5kcRYJSMaMOCCwQ"}]
            })
            response = self.client.get("/attractions/by_coordinates?latitude=48.8566&longitude=2.3522&category=touristique")
            self.assertEqual(response.status_code, 200)
            self.assertIn("attraction", response.json())

    def test_get_attractions_by_coordinates_not_found(self):
        with patch('app.routers.attractions.PlacesService') as MockService:
            instance = MockService.return_value
            instance.get_tourist_attractions_nearby = AsyncMock(return_value=None)
            response = self.client.get("/attractions/by_coordinates?latitude=48.8566&longitude=2.3522&category=touristique")
            self.assertEqual(response.status_code, 404)
            self.assertIn("ATTRACTION_NOT_FOUND", response.json()["error"])


class TestGetAttraction(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_get_attraction_by_name_success(self):
        with patch('app.routers.attraction.PlacesService') as MockService:
            instance = MockService.return_value
            instance.get_place_id = AsyncMock(return_value="ChIJD7fiBh9u5kcRYJSMaMOCCwQ")
            instance.get_tourist_attraction = AsyncMock(return_value={
                "attraction": {"name": "Tour Eiffel", "address": "Paris", "place_id": "ChIJD7fiBh9u5kcRYJSMaMOCCwQ"}
            })
            response = self.client.get("/attraction/by_name?place_name=Tour+Eiffel&address=Paris")
            self.assertEqual(response.status_code, 200)
            self.assertIn("attraction", response.json())

    def test_get_attraction_by_name_with_session_token(self):
        with patch('app.routers.attraction.PlacesService') as MockService:
            instance = MockService.return_value
            instance.get_place_id = AsyncMock(return_value="ChIJD7fiBh9u5kcRYJSMaMOCCwQ")
            instance.get_tourist_attraction = AsyncMock(return_value={
                "attraction": {"name": "Tour Eiffel", "address": "Paris", "place_id": "ChIJD7fiBh9u5kcRYJSMaMOCCwQ"}
            })
            response = self.client.get(
                "/attraction/by_name?place_name=Tour+Eiffel&address=Paris&session_token=abc-123-session"
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn("attraction", response.json())
            instance.get_tourist_attraction.assert_called_once_with(
                "ChIJD7fiBh9u5kcRYJSMaMOCCwQ",
                session_token="abc-123-session",
                user_id="febfedf3-f6fc-4043-8dce-daf2d2b95906"
            )

    def test_get_attraction_by_name_not_found(self):
        with patch('app.routers.attraction.PlacesService') as MockService:
            instance = MockService.return_value
            instance.get_place_id = AsyncMock(return_value=None)
            response = self.client.get("/attraction/by_name?place_name=Inconnu&address=Inconnu")
            self.assertEqual(response.status_code, 404)
            self.assertIn("PLACE_NOT_FOUND", response.json()["error"])

    def test_get_attraction_by_coordinates_success(self):
        with patch('app.routers.attraction.PlacesService') as MockService:
            instance = MockService.return_value
            instance.get_place_id_from_coordinates = AsyncMock(return_value="ChIJD7fiBh9u5kcRYJSMaMOCCwQ")
            instance.get_tourist_attraction = AsyncMock(return_value={
                "attraction": {"name": "Tour Eiffel", "address": "Paris", "place_id": "ChIJD7fiBh9u5kcRYJSMaMOCCwQ"}
            })
            response = self.client.get("/attraction/by_coordinates?latitude=48.8566&longitude=2.3522")
            self.assertEqual(response.status_code, 200)
            self.assertIn("attraction", response.json())

    def test_get_attraction_by_coordinates_not_found(self):
        with patch('app.routers.attraction.PlacesService') as MockService:
            instance = MockService.return_value
            instance.get_place_id_from_coordinates = AsyncMock(return_value=None)
            response = self.client.get("/attraction/by_coordinates?latitude=0.0&longitude=0.0")
            self.assertEqual(response.status_code, 404)
            self.assertIn("PLACE_NOT_FOUND", response.json()["error"])


if __name__ == '__main__':
    unittest.main(verbosity=2)