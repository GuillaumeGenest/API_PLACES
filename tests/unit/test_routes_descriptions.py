import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app


class TestGetDescriptions(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_get_description_success(self):
        with patch('app.routers.descriptions.AIService') as MockService:
            instance = MockService.return_value
            instance.generate_description = AsyncMock(return_value="Monument emblématique de Paris construit en 1889.")
            response = self.client.get("/descriptions/?place_name=Tour+Eiffel&address=Paris")
            self.assertEqual(response.status_code, 200)
            self.assertTrue(len(response.text.strip()) > 0)

    def test_get_description_failure(self):
        with patch('app.routers.descriptions.AIService') as MockService:
            instance = MockService.return_value
            instance.generate_description = AsyncMock(return_value=None)
            response = self.client.get("/descriptions/?place_name=LieuInexistant")
            self.assertEqual(response.status_code, 404)
            self.assertIn("DESCRIPTION_NOT_FOUND", response.json()["error"])


if __name__ == '__main__':
    unittest.main(verbosity=2)