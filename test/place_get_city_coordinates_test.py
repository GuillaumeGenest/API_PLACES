import unittest
from unittest.mock import patch, Mock
import sys
import os

# Ajouter le chemin absolu du dossier contenant API_Places.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from API_Places import *
import time

from ConfigurationTest import CustomTestResult



class TestGetCityCoordinates(unittest.TestCase):
    def setUp(self):
        # Données de test pour simuler les réponses de l'API
        self.paris_response = {
            'results': [{
                'geometry': {
                    'location': {
                        'lat': 48.8566,
                        'lng': 2.3522
                    }
                }
            }]
        }
        
        self.empty_response = {
            'results': []
        }
        
        self.error_response = {
            'status': 'ZERO_RESULTS',
            'results': []
        }

    @patch('requests.get')
    def test_valid_city(self, mock_get):
        # Configuration du mock pour une ville valide
        mock_get.return_value.json.return_value = self.paris_response
        mock_get.return_value.status_code = 200

        # Test avec une ville valide
        latitude, longitude = get_city_coordinates("Paris")
        
        # Vérifications
        self.assertEqual(latitude, 48.8566)
        self.assertEqual(longitude, 2.3522)
        
        # Vérification que l'API a été appelée avec les bons paramètres
        mock_get.assert_called_once_with(
            "https://maps.googleapis.com/maps/api/geocode/json",
            params={
                "address": "Paris",
                "key": GOOGLE_API_KEY,
                "language": "fr"
            }
        )

    @patch('requests.get')
    def test_city_not_found(self, mock_get):
        # Configuration du mock pour une ville non trouvée
        mock_get.return_value.json.return_value = self.empty_response
        mock_get.return_value.status_code = 200

        # Test avec une ville invalide
        result = get_city_coordinates("VilleInexistante")
        
        # Vérification
        self.assertIsNone(result)

    @patch('requests.get')
    def test_api_error(self, mock_get):
        # Simulation d'une erreur d'API
        mock_get.side_effect = requests.exceptions.RequestException("Erreur API")

        # Test avec une erreur d'API
        with self.assertRaises(requests.exceptions.RequestException):
            get_city_coordinates("Paris")

    @patch('requests.get')
    def test_invalid_response_format(self, mock_get):
        # Configuration du mock pour une réponse invalide
        mock_get.return_value.json.return_value = {"invalid": "format"}
        mock_get.return_value.status_code = 200

        # Test avec une réponse de format invalide
        try:
            result = get_city_coordinates("Paris")
        except KeyError:
            # Vérifie que la fonction lève une KeyError pour gérer la réponse invalide
            return
        else:
            # Si la fonction ne lève pas d'exception, le test échoue
            self.fail("La fonction n'a pas levé de KeyError pour une réponse invalide")

if __name__ == '__main__':

    print("###############################################################")
    print("Lancement des tests unitaires -------   get_city_coordinates   --------")                
    print("###############################################################")

    # Création du test runner personnalisé
    runner = unittest.TextTestRunner(resultclass=CustomTestResult)
    unittest.main(testRunner=runner, verbosity=2)