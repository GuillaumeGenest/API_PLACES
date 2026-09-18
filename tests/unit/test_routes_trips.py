import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.core.exceptions import TooManyConcurrentGenerationsError
from app.main import app


MOCK_CITY_TRIP = {
    "lieux": [
        {
            "id": "1",
            "locationName": "Tour Eiffel",
            "locationAdress": "Champ de Mars, 5 Av. Anatole France, 75007 Paris",
            "countryCode": "FR",
            "latitude": 48.8584,
            "longitude": 2.2945,
            "date": "2024-06-01T09:00:00"
        },
        {
            "id": "2",
            "locationName": "Musée du Louvre",
            "locationAdress": "Rue de Rivoli, 75001 Paris",
            "countryCode": "FR",
            "latitude": 48.8606,
            "longitude": 2.3376,
            "date": "2024-06-01T14:00:00"
        }
    ]
}

MOCK_ROAD_TRIP = {
    "villes": [
        {
            "id": "1",
            "locationName": "Paris",
            "locationAdress": "Paris, France",
            "countryCode": "FR",
            "latitude": 48.8566,
            "longitude": 2.3522,
            "date": "2024-06-01T09:00:00"
        }
    ],
    "lieux": [
        {
            "id": "2",
            "locationName": "Tour Eiffel",
            "locationAdress": "Champ de Mars, 75007 Paris",
            "countryCode": "FR",
            "latitude": 48.8584,
            "longitude": 2.2945,
            "date": "2024-06-01T10:00:00"
        }
    ]
}


class TestCityTrip(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_city_trip_success(self):
        with patch('app.routers.trips.TripService') as MockService:
            instance = MockService.return_value
            instance.generate_city_trip = AsyncMock(return_value=MOCK_CITY_TRIP)
            response = self.client.get("/trips/city?city_name=Paris&firstdate=2024-06-01&lastdate=2024-06-03")
            self.assertEqual(response.status_code, 200)
            self.assertIn("lieux", response.json())
            self.assertEqual(len(response.json()["lieux"]), 2)

    def test_city_trip_failure(self):
        with patch('app.routers.trips.TripService') as MockService:
            instance = MockService.return_value
            instance.generate_city_trip = AsyncMock(return_value=None)
            response = self.client.get("/trips/city?city_name=Paris&firstdate=2024-06-01&lastdate=2024-06-03")
            self.assertEqual(response.status_code, 400)
            self.assertIn("Erreur lors de la génération du trip", response.json()["detail"])

    def test_city_trip_invalid_dates(self):
        response = self.client.get("/trips/city?city_name=Paris&firstdate=2024-06-05&lastdate=2024-06-01")
        self.assertEqual(response.status_code, 400)
        self.assertIn("La date de début doit être avant la date de fin", response.json()["detail"])

    def test_city_trip_same_dates(self):
        with patch('app.routers.trips.TripService') as MockService:
            instance = MockService.return_value
            instance.generate_city_trip = AsyncMock(return_value=MOCK_CITY_TRIP)
            response = self.client.get("/trips/city?city_name=Paris&firstdate=2024-06-01&lastdate=2024-06-01")
            self.assertEqual(response.status_code, 200)

    def test_city_trip_missing_params(self):
        response = self.client.get("/trips/city?city_name=Paris")
        self.assertEqual(response.status_code, 422)

    def test_city_trip_internal_exception_hides_details(self):
        with patch('app.api.API_Trip.client') as mock_client:
            mock_client.responses.create = AsyncMock(side_effect=Exception("db password leaked: hunter2"))
            response = self.client.get("/trips/city?city_name=Paris&firstdate=2024-06-01&lastdate=2024-06-03")
            self.assertEqual(response.status_code, 500)
            self.assertNotIn("hunter2", response.text)
            self.assertEqual(response.json()["detail"], "Erreur serveur interne")

    def test_city_trip_too_many_concurrent_requests(self):
        with patch('app.routers.trips.TripService') as MockService:
            instance = MockService.return_value
            instance.generate_city_trip = AsyncMock(side_effect=TooManyConcurrentGenerationsError())
            response = self.client.get("/trips/city?city_name=Paris&firstdate=2024-06-01&lastdate=2024-06-03")
            self.assertEqual(response.status_code, 429)
            self.assertIn("TOO_MANY_CONCURRENT_REQUESTS", response.json()["error"])


class TestRoadTrip(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_road_trip_success(self):
        with patch('app.routers.trips.TripService') as MockService:
            instance = MockService.return_value
            instance.generate_road_trip = AsyncMock(return_value=MOCK_ROAD_TRIP)
            response = self.client.get("/trips/roadtrip?region=Paris&firstdate=2024-06-01&lastdate=2024-06-07")
            self.assertEqual(response.status_code, 200)
            self.assertIn("villes", response.json())
            self.assertIn("lieux", response.json())

    def test_road_trip_failure(self):
        with patch('app.routers.trips.TripService') as MockService:
            instance = MockService.return_value
            instance.generate_road_trip = AsyncMock(return_value=None)
            response = self.client.get("/trips/roadtrip?region=Paris&firstdate=2024-06-01&lastdate=2024-06-07")
            self.assertEqual(response.status_code, 400)
            self.assertIn("Erreur lors de la génération du road trip", response.json()["detail"])

    def test_road_trip_invalid_dates(self):
        response = self.client.get("/trips/roadtrip?region=Paris&firstdate=2024-06-07&lastdate=2024-06-01")
        self.assertEqual(response.status_code, 400)
        self.assertIn("La date de début doit être avant la date de fin", response.json()["detail"])

    def test_road_trip_same_dates(self):
        with patch('app.routers.trips.TripService') as MockService:
            instance = MockService.return_value
            instance.generate_road_trip = AsyncMock(return_value=MOCK_ROAD_TRIP)
            response = self.client.get("/trips/roadtrip?region=Paris&firstdate=2024-06-01&lastdate=2024-06-01")
            self.assertEqual(response.status_code, 200)

    def test_road_trip_missing_params(self):
        response = self.client.get("/trips/roadtrip?region=Paris")
        self.assertEqual(response.status_code, 422)

    def test_road_trip_internal_exception_hides_details(self):
        with patch('app.api.API_Trip.client') as mock_client:
            mock_client.responses.create = AsyncMock(side_effect=Exception("db password leaked: hunter2"))
            response = self.client.get("/trips/roadtrip?region=Paris&firstdate=2024-06-01&lastdate=2024-06-07")
            self.assertEqual(response.status_code, 500)
            self.assertNotIn("hunter2", response.text)
            self.assertEqual(response.json()["detail"], "Erreur serveur interne")

    def test_road_trip_too_many_concurrent_requests(self):
        with patch('app.routers.trips.TripService') as MockService:
            instance = MockService.return_value
            instance.generate_road_trip = AsyncMock(side_effect=TooManyConcurrentGenerationsError())
            response = self.client.get("/trips/roadtrip?region=Paris&firstdate=2024-06-01&lastdate=2024-06-07")
            self.assertEqual(response.status_code, 429)
            self.assertIn("TOO_MANY_CONCURRENT_REQUESTS", response.json()["error"])


if __name__ == '__main__':
    unittest.main(verbosity=2)