import unittest
from unittest.mock import patch, Mock
import sys
import os

# Ajouter le chemin absolu du dossier contenant API_Places.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from API_Places import *
import time

from ConfigurationTest import CustomTestResult

class TestGetTouristAttraction(unittest.TestCase):
    @patch('requests.get')
    def test_get_tourist_attraction_success(self, mock_get):
        # Configurer une réponse simulée pour un cas réussi
        mock_response = Mock()
        mock_response.raise_for_status = Mock()  # Aucun effet si le statut est 200
        mock_response.json.return_value = {
            "id": "test_id",
            "displayName": {"text": "Tour Eiffel"},
            "location": {"latitude": 48.8584, "longitude": 2.2945},
            "formattedAddress": "Champ de Mars, 5 Avenue Anatole France, 75007 Paris, France",
            "rating": 4.6,
            "userRatingCount": 100000,
            "photos": [{"name": "photo_reference"}],
            "websiteUri": "https://www.toureiffel.paris",
            "googleMapsUri": "https://g.page/TourEiffel",
            "internationalPhoneNumber": "+33 892 70 12 39",
            "editorialSummary": {"text": "Une tour emblématique de Paris."},
            "regularOpeningHours": {"weekdayDescriptions": ["Lundi: 9:00 AM – 12:00 AM"]}
        }
        mock_get.return_value = mock_response

        # Appeler la fonction avec un place_id fictif
        result = get_tourist_attraction("test_id")

        # Vérifier le résultat
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], "Tour Eiffel")
        self.assertEqual(result[0]['address'], "Champ de Mars, 5 Avenue Anatole France, 75007 Paris, France")
        self.assertEqual(result[0]['latitude'], 48.8584)
        self.assertEqual(result[0]['longitude'], 2.2945)
        self.assertEqual(result[0]['rating'], 4.6)
        self.assertEqual(result[0]['user_ratings_total'], 100000)
        self.assertIn("https://places.googleapis.com/v1/photo_reference/media?key=", result[0]['photo_urls'][0])
        self.assertEqual(result[0]['website'], "https://www.toureiffel.paris")
        self.assertEqual(result[0]['google_maps_url'], "https://g.page/TourEiffel")
        self.assertEqual(result[0]['phone'], "+33 892 70 12 39")
        self.assertEqual(result[0]['description'], "Une tour emblématique de Paris.")
        self.assertEqual(result[0]['opening_hours'], ["Lundi: 9:00 AM – 12:00 AM"])

    @patch('requests.get')
    def test_get_tourist_attraction_failure(self, mock_get):
        # Configurer une réponse simulée pour un cas d'erreur
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Erreur 404")
        mock_get.return_value = mock_response

        # Appeler la fonction avec un place_id fictif qui provoque une erreur
        result = get_tourist_attraction("invalid_id")

        # Vérifier que le résultat est None en cas d'échec de la requête
        self.assertIsNone(result)


    @patch('requests.get')
    def test_api_error(self, mock_get):
        # Simule une erreur d'API
        mock_get.side_effect = requests.exceptions.RequestException("Erreur API")

        # Appeler la fonction avec un place_id fictif et vérifier qu'une exception est gérée
        result = get_tourist_attraction("test_id_erreur")

        # Vérifier que le résultat est None en cas d'erreur d'API
        self.assertIsNone(result)

if __name__ == '__main__':
    print("###############################################################")
    print("Lancement des tests unitaires -------   get_tourist_attraction   --------")                
    print("###############################################################")

    # Création du test runner personnalisé
    runner = unittest.TextTestRunner(resultclass=CustomTestResult)
    unittest.main(testRunner=runner, verbosity=2)