import unittest
from unittest.mock import patch, Mock
import sys
import os

# Ajouter le chemin absolu du dossier contenant API_Places.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from API_Places import *
from ConfigurationTest import CustomTestResult

###############################################################
#               test unitaire 
###############################################################


class TestGetTouristAttractionsNearby(unittest.TestCase):
    @patch('requests.post')
    def test_get_tourist_attractions_nearby_success(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "places": [
                {
                    "displayName": {"text": "Tour Eiffel"},
                    "formattedAddress": "Champ de Mars, 5 Avenue Anatole France, 75007 Paris, France",
                    "id": "ChIJD7fiBh9u5kcRYJSMaMOCCwQ",
                    "location": {"latitude": 48.8588443, "longitude": 2.2943506},
                    "rating": 4.7,
                    "userRatingCount": 12000,
                    "photos": [{"name": "photo_reference"}],
                    "websiteUri": "http://www.toureiffel.paris",
                    "googleMapsUri": "https://g.page/TourEiffel",
                    "internationalPhoneNumber": "+33 1 23 45 67 89",
                    "editorialSummary": {"text": "Monument emblématique de Paris"},
                    "regularOpeningHours": {"weekdayDescriptions": ["Lundi: 9:00 - 23:00"]}
                }
            ]
        }
        mock_post.return_value = mock_response

        lat, lng, radius = 48.8588443, 2.2943506, 5000
        result = get_tourist_attractions_nearby(lat, lng, radius)

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], "Tour Eiffel")
        self.assertEqual(result[0]['address'], "Champ de Mars, 5 Avenue Anatole France, 75007 Paris, France")
        self.assertEqual(result[0]['rating'], 4.7)
        self.assertEqual(result[0]['google_maps_url'], "https://g.page/TourEiffel")
        self.assertTrue(result[0]['photo_urls'][0].startswith("https://places.googleapis.com/v1/photo_reference/media?key="))

    @patch('requests.post')
    def test_get_tourist_attractions_nearby_no_places_found(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "places": []
        }
        mock_post.return_value = mock_response

        lat, lng, radius = 48.8588443, 2.2943506, 5000
        result = get_tourist_attractions_nearby(lat, lng, radius)

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

    @patch('requests.post')
    def test_get_tourist_attractions_nearby_api_error(self, mock_post):
        # Création de la réponse simulée
        mock_response = Mock()
        mock_response.status_code = 403  # Erreur 403 (Forbidden)
        mock_response.json.return_value = {}  # Réponse JSON vide pour l'erreur
        mock_post.return_value = mock_response

        lat, lng, radius = 48.8588443, 2.2943506, 5000
        result = get_tourist_attractions_nearby(lat, lng, radius)

        # Vérifie que le résultat est None en cas d'erreur API
        self.assertIsNone(result)

    @patch('requests.post')
    def test_get_tourist_attractions_nearby_partial_data(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "places": [
                {
                    "displayName": {"text": "Louvre Museum"},
                    "formattedAddress": "Rue de Rivoli, 75001 Paris, France",
                    "id": "ChIJLU7jZClu5kcR4PcOOO6p3I0",
                    "location": {"latitude": 48.8606, "longitude": 2.3376},
                    "googleMapsUri": "https://g.page/Louvre"
                }
            ]
        }
        mock_post.return_value = mock_response

        lat, lng, radius = 48.8606, 2.3376, 5000
        result = get_tourist_attractions_nearby(lat, lng, radius)

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], "Louvre Museum")
        self.assertEqual(result[0]['address'], "Rue de Rivoli, 75001 Paris, France")
        self.assertEqual(result[0]['rating'], "Non notée") 

if __name__ == '__main__':

    print("###############################################################")
    print("Lancement des tests unitaires -------   get_tourist_attractions_nearby   --------")                
    print("###############################################################")

    # Création du test runner personnalisé
    runner = unittest.TextTestRunner(resultclass=CustomTestResult)
    unittest.main(testRunner=runner, verbosity=2)