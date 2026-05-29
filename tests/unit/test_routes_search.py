import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app

MOCK_PREDICTIONS = [
    {
        "place_id": "ChIJu46S-ZZhLxMROG5lkwZ3D7k",
        "name": "Rome, Ville métropolitaine de Rome Capitale, Italie",
        "main_text": "Rome",
        "secondary_text": "Ville métropolitaine de Rome Capitale, Italie"
    },
    {
        "place_id": "ChIJw0rXGxGKJRMRAIE4sppPCQM",
        "name": "Rome, Italie",
        "main_text": "Rome",
        "secondary_text": "Italie"
    }
]


class TestAutocomplete(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_autocomplete_success(self):
        with patch('app.routers.search.AutocompleteService') as MockService:
            instance = MockService.return_value
            instance.autocomplete = AsyncMock(return_value=MOCK_PREDICTIONS)
            response = self.client.get("/search/autocomplete?input=Rome")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json()), 2)
            self.assertIn("place_id", response.json()[0])
            self.assertIn("main_text", response.json()[0])
            self.assertIn("secondary_text", response.json()[0])

    def test_autocomplete_with_session_token(self):
        with patch('app.routers.search.AutocompleteService') as MockService:
            instance = MockService.return_value
            instance.autocomplete = AsyncMock(return_value=MOCK_PREDICTIONS)
            response = self.client.get(
                "/search/autocomplete?input=Rome&session_token=3519edfe-0f75-4a30-bfe4-7cbd89340b2c"
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json()), 2)

    def test_autocomplete_input_trop_court(self):
        response = self.client.get("/search/autocomplete?input=Rom")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_autocomplete_input_vide(self):
        response = self.client.get("/search/autocomplete?input=")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_autocomplete_aucun_resultat(self):
        with patch('app.routers.search.AutocompleteService') as MockService:
            instance = MockService.return_value
            instance.autocomplete = AsyncMock(return_value=[])
            response = self.client.get("/search/autocomplete?input=Xyzabc")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), [])

    def test_autocomplete_langue_personnalisee(self):
        with patch('app.routers.search.AutocompleteService') as MockService:
            instance = MockService.return_value
            instance.autocomplete = AsyncMock(return_value=MOCK_PREDICTIONS)
            response = self.client.get("/search/autocomplete?input=Rome&language=en")
            self.assertEqual(response.status_code, 200)

    def test_autocomplete_missing_input(self):
        response = self.client.get("/search/autocomplete")
        self.assertEqual(response.status_code, 422)


if __name__ == '__main__':
    unittest.main(verbosity=2)