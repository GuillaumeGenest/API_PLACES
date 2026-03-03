import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app


class TestGetAIAttraction(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_get_ai_attraction_success(self):
        with patch('app.routers.ai.AIService') as MockService:
            instance = MockService.return_value
            instance.generate_attraction.return_value = {
                "attraction": [{
                    "name": "Tour Eiffel",
                    "address": "Paris",
                    "place_id": "ai_abc123",
                    "latitude": 48.8566,
                    "longitude": 2.3522,
                    "rating": 4.7,
                    "user_ratings_total": 12000,
                    "photo_urls": [],
                    "website": "http://www.toureiffel.paris",
                    "google_maps_url": "Non disponible",
                    "phone": "+33 1 23 45 67 89",
                    "description": "Monument emblématique de Paris",
                    "opening_hours": ["Lundi: 09:00 - 23:00"],
                    "category": "touristique"
                }]
            }
            response = self.client.get("/ai/attraction?place_name=Tour+Eiffel&address=Paris&category=touristique")
            self.assertEqual(response.status_code, 200)
            self.assertIn("attraction", response.json())

    def test_get_ai_attraction_failure(self):
        with patch('app.routers.ai.AIService') as MockService:
            instance = MockService.return_value
            instance.generate_attraction.return_value = None
            response = self.client.get("/ai/attraction?place_name=LieuInexistant")
            self.assertEqual(response.status_code, 400)
            self.assertIn("AI_GENERATION_ERROR", response.json()["error"])


if __name__ == '__main__':
    unittest.main(verbosity=2)