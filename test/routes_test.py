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

    # @patch('API_Places.get_city_coordinates')
    # @patch('API_Places.get_tourist_attractions_nearby')
    # def test_get_attractions_no_attractions_found(self, mock_get_tourist_attractions_nearby, mock_get_city_coordinates):
    #     mock_get_city_coordinates.return_value = (48.8566, 2.3522)
    #     mock_get_tourist_attractions_nearby.return_value = []

    #     response = self.client.get("/attractions/Paris")
    #     self.assertEqual(response.status_code, 404)
    #     self.assertIn("Aucune attraction trouvée", response.json()["detail"])

    @patch('API_Places.get_place_id')
    @patch('API_Places.get_tourist_attraction')
    def test_get_attraction_information_success(self, mock_get_tourist_attraction, mock_get_place_id):
        mock_get_place_id.return_value = "test_id"
        mock_get_tourist_attraction.return_value = {"name": "Tour Eiffel", "address": "Paris"}

        response = self.client.get("/attraction?place_name=Tour+Eiffel&address=Paris")
        self.assertEqual(response.status_code, 200)
        self.assertIn("attraction", response.json())

    # @patch('API_Places.get_place_id')
    # def test_get_attraction_information_place_not_found(self, mock_get_place_id):
    #     mock_get_place_id.return_value = None

    #     response = self.client.get("/attraction/AttractionInexistante")
    #     self.assertEqual(response.status_code, 400)
    #     self.assertIn("Erreur dans les coordonnées de la ville", response.json()["detail"])

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


if __name__ == '__main__':

    print("###############################################################")
    print("Lancement des tests unitaires -------   routes   --------")                
    print("###############################################################")

    # Création du test runner personnalisé
    runner = unittest.TextTestRunner(resultclass=CustomTestResult)
    unittest.main(testRunner=runner, verbosity=2)