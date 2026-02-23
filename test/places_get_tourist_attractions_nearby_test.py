import unittest
from unittest.mock import patch, Mock
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Définir l'environnement de test avant d'importer les modules
os.environ['ENVIRONMENT'] = 'testing'
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
        result = get_tourist_attractions_nearby(lat, lng, AttractionCategory.touristique, radius)
        self.assertEqual(result["attraction"][0]["name"], "Tour Eiffel")
        self.assertEqual(result["attraction"][0]["address"], "Champ de Mars, 5 Avenue Anatole France, 75007 Paris, France")
        self.assertEqual(result["attraction"][0]["place_id"], "ChIJD7fiBh9u5kcRYJSMaMOCCwQ")
        self.assertEqual(result["attraction"][0]["latitude"], 48.8588443)
        self.assertEqual(result["attraction"][0]["longitude"], 2.2943506)
        self.assertEqual(result["attraction"][0]["rating"], 4.7)
        self.assertEqual(result["attraction"][0]["user_ratings_total"], 12000)
        self.assertEqual(result["attraction"][0]["google_maps_url"], "https://g.page/TourEiffel")
        self.assertEqual(result["attraction"][0]["phone"], "+33 1 23 45 67 89")

    

    @patch('requests.post')
    def test_get_tourist_attractions_nearby_no_places_found(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "places": []
        }
        mock_post.return_value = mock_response

        lat, lng, radius = 48.8588443, 2.2943506, 5000
        result = get_tourist_attractions_nearby(lat, lng, AttractionCategory.touristique, radius)
        self.assertEqual(result, {"attraction": []})

    @patch('requests.post')
    def test_get_tourist_attractions_nearby_api_error(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.json.return_value = {}  # Réponse vide pour l'erreur
        mock_post.return_value = mock_response

        lat, lng, radius = 48.8588443, 2.2943506, 5000
        result = get_tourist_attractions_nearby(lat, lng, AttractionCategory.touristique, radius)

        # Vérifie que le résultat est vide quand l'API renvoie une erreur
        self.assertEqual(result, {"attraction": []})

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
        result = get_tourist_attractions_nearby(lat, lng, AttractionCategory.touristique, radius)
        self.assertIn("Louvre Museum", result["attraction"][0]["name"])
        self.assertEqual(len(result), 1)
        self.assertEqual(result["attraction"][0]['name'], "Louvre Museum")
        self.assertEqual(result["attraction"][0]['address'], "Rue de Rivoli, 75001 Paris, France")
        self.assertEqual(result["attraction"][0]['rating'], "Non notée") 
        


if __name__ == '__main__':

    print("###############################################################")
    print("Lancement des tests unitaires -------   get_tourist_attractions_nearby   --------")                
    print("###############################################################")

    # Création du test runner personnalisé
    runner = unittest.TextTestRunner(resultclass=CustomTestResult)
    unittest.main(testRunner=runner, verbosity=2)