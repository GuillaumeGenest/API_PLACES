import unittest
from fastapi.testclient import TestClient
from unittest.mock import patch

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Définir l'environnement de test avant d'importer les modules
os.environ['ENVIRONMENT'] = 'testing'
from API_Places import *
import time
from routes import app
from ConfigurationTest import CustomTestResult


class TestAttractionsAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    @patch('API_Places.get_city_coordinates')
    @patch('API_Places.get_tourist_attractions_nearby')
    def test_get_attractions_success(self, mock_get_tourist_attractions_nearby, mock_get_city_coordinates):
        mock_get_city_coordinates.return_value = (48.8566, 2.3522)
        mock_get_tourist_attractions_nearby.return_value = [{"name": "Tour Eiffel", "address": "Paris"}]

        response = self.client.get("/attractions?city_name=Paris&category=touristique")
        self.assertEqual(response.status_code, 200)
        self.assertIn("attraction", response.json())

    @patch('routes.get_city_coordinates')
    def test_get_attractions_city_not_found(self, mock_get_city_coordinates):
        mock_get_city_coordinates.return_value = None
        print(f"mock_get_city_coordinates.return_value = {mock_get_city_coordinates.return_value}")
        response = self.client.get("/attractions?city_name=Unknoww&category=touristique")
        print(f"response.status_code = {response.status_code}")
        print(f"response.json() = {response.json()}")
        self.assertEqual(response.status_code, 400)

    @patch('routes.get_tourist_attraction')
    @patch('routes.get_place_id')
    def test_get_attraction_information_success(self, mock_get_place_id, mock_get_tourist_attraction):
        mock_get_place_id.return_value = "ChIJD7fiBh9u5kcRYJSMaMOCCwQ"
        mock_get_tourist_attraction.return_value = {"attraction": {"name": "Tour Eiffel", "address": "Paris"}}
        response = self.client.get("/attraction?place_name=Tour+Eiffel&address=Paris")
        self.assertEqual(response.status_code, 200)
        self.assertIn("attraction", response.json())

    @patch('API_Places.get_place_id_from_coordinates')
    @patch('API_Places.get_tourist_attraction')
    def test_get_attraction_information_by_coordinates_success(
            self, mock_get_place_id_from_coordinates, mock_get_tourist_attraction):
        mock_get_place_id_from_coordinates.return_value = "test_id"
        mock_get_tourist_attraction.return_value = {"name": "Tour Eiffel", "address": "Paris"}

        response = self.client.get("/attraction_with_coordinates?latitude=48.8566&longitude=2.3522")
        self.assertEqual(response.status_code, 200)
        self.assertIn("attraction", response.json())

    @patch('API_Places.get_place_id_from_coordinates')
    def test_get_attraction_information_by_coordinates_place_not_found(self, mock_get_place_id_from_coordinates):
        mock_get_place_id_from_coordinates.return_value = None

        response = self.client.get("/attraction_with_coordinates?latitude=0.0&longitude=0.0")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Erreur dans les coordonnées de la ville", response.json()["detail"])

    @patch('routes.generate_attraction')
    def test_get_ai_attraction_failure(self, mock_generate_attraction):
        mock_generate_attraction.return_value = None
        response = self.client.get("/generate_attraction?place_name=LieuInexistant")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Erreur lors de la génération IA", response.json()["detail"])

    @patch('routes.generate_attraction')
    def test_get_ai_attraction_success(self, mock_generate_attraction):
        mock_generate_attraction.return_value = {
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
        response = self.client.get("/generate_attraction?place_name=Tour+Eiffel&address=Paris&category=touristique")
        self.assertEqual(response.status_code, 200)
        self.assertIn("attraction", response.json())

    @patch('routes.generate_description')
    def test_generate_description_success(self, mock_generate_description):
        mock_generate_description.return_value = (
            "Monument emblématique de Paris construit en 1889. "
            "Il offre une vue panoramique sur la capitale. "
            "C'est l'un des sites les plus visités au monde."
        )

        response = self.client.get("/generate_description?place_name=Tour+Eiffel&address=Paris")

        print(f"[DEBUG] response.text = {response.text}")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.text.strip()) > 0)

    @patch('routes.generate_description')
    def test_generate_description_failure(self, mock_generate_description):
        mock_generate_description.return_value = None

        response = self.client.get("/generate_description?place_name=LieuInexistant")

        self.assertEqual(response.status_code, 404)
        self.assertIn("Impossible de générer une description", response.json()["detail"])

    # --- Tests /generate_url_image/place ---

    @patch('routes.get_url_image_from_wikipedia')
    def test_get_url_image_by_place_success(self, mock_get_url_image_from_wikipedia):
        mock_get_url_image_from_wikipedia.return_value = "http://example.com/photo.jpg"

        response = self.client.get("/generate_url_image/place?place=Tour+Eiffel")

        print(f"[DEBUG] response.status_code = {response.status_code}")
        print(f"[DEBUG] response.text = {response.text}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, "http://example.com/photo.jpg")

    @patch('routes.get_url_image_from_wikipedia')
    def test_get_url_image_by_place_not_found(self, mock_get_url_image_from_wikipedia):
        mock_get_url_image_from_wikipedia.return_value = None

        response = self.client.get("/generate_url_image/place?place=Inconnu")

        print(f"[DEBUG] response.status_code = {response.status_code}")
        print(f"[DEBUG] response.json() = {response.json()}")

        self.assertEqual(response.status_code, 404)
        self.assertIn("Aucun url trouvé", response.json()["detail"])

    # --- Tests /get_url_image/place_and_address ---

    @patch('routes.get_url_image_from_google')
    @patch('routes.get_place_id')
    def test_get_url_image_by_place_and_address_success(
        self,
        mock_get_place_id,              # dernier @patch = premier arg
        mock_get_url_image_from_google  # premier @patch = second arg
    ):
        mock_get_place_id.return_value = "test_place_id"
        mock_get_url_image_from_google.return_value = "http://example.com/photo.jpg"

        response = self.client.get("/get_url_image/place_and_address?place_name=Tour+Eiffel&address=Paris")

        print(f"[DEBUG] response.status_code = {response.status_code}")
        print(f"[DEBUG] response.text = {response.text}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, "http://example.com/photo.jpg")

    @patch('routes.get_place_id')
    def test_get_url_image_by_place_and_address_place_not_found(self, mock_get_place_id):
        mock_get_place_id.return_value = None

        response = self.client.get("/get_url_image/place_and_address?place_name=Inconnu")

        print(f"[DEBUG] response.status_code = {response.status_code}")
        print(f"[DEBUG] response.json() = {response.json()}")

        self.assertEqual(response.status_code, 400)
        self.assertIn("Erreur dans le nom du lieu", response.json()["detail"])

    @patch('routes.get_url_image_from_google')
    @patch('routes.get_place_id')
    def test_get_url_image_by_place_and_address_no_photo(
        self,
        mock_get_place_id,              # dernier @patch = premier arg
        mock_get_url_image_from_google  # premier @patch = second arg
    ):
        mock_get_place_id.return_value = "test_place_id"
        mock_get_url_image_from_google.return_value = None

        response = self.client.get("/get_url_image/place_and_address?place_name=Tour+Eiffel&address=Paris")

        print(f"[DEBUG] response.status_code = {response.status_code}")
        print(f"[DEBUG] response.json() = {response.json()}")

        self.assertEqual(response.status_code, 404)
        self.assertIn("Aucun url trouvé", response.json()["detail"])

    # --- Tests /get_url_image/id ---

    def test_get_url_image_by_id_missing_id(self):
        response = self.client.get("/get_url_image/id?place_id=")

        print(f"[DEBUG] response.status_code = {response.status_code}")
        print(f"[DEBUG] response.json() = {response.json()}")

        self.assertEqual(response.status_code, 400)
        self.assertIn("place_id manquant", response.json()["detail"])

    @patch('routes.get_url_image_from_google')
    def test_get_url_image_by_id_success(self, mock_get_url_image_from_google):
        mock_get_url_image_from_google.return_value = "http://example.com/photo.jpg"

        response = self.client.get("/get_url_image/id?place_id=test_place_id")

        print(f"[DEBUG] response.status_code = {response.status_code}")
        print(f"[DEBUG] response.text = {response.text}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, "http://example.com/photo.jpg")

    @patch('routes.get_url_image_from_google')
    def test_get_url_image_by_id_no_photo(self, mock_get_url_image_from_google):
        mock_get_url_image_from_google.return_value = None

        response = self.client.get("/get_url_image/id?place_id=test_place_id")

        print(f"[DEBUG] response.status_code = {response.status_code}")
        print(f"[DEBUG] response.json() = {response.json()}")

        self.assertEqual(response.status_code, 404)
        self.assertIn("Aucun url trouvé", response.json()["detail"])


if __name__ == '__main__':

    print("###############################################################")
    print("Lancement des tests unitaires -------   routes   --------")
    print("###############################################################")

    runner = unittest.TextTestRunner(resultclass=CustomTestResult)
    unittest.main(testRunner=runner, verbosity=2)