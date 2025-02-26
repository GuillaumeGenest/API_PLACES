import unittest
from unittest.mock import patch, Mock
import sys
import os

import os
import unittest
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import *
# Définir l'environnement de test avant d'importer les modules
os.environ['ENVIRONMENT'] = 'testing'
GOOGLE_API_KEY = get_api_key()
print(f"Clé API utilisée pour les tests: {GOOGLE_API_KEY}") 
# Ajouter le chemin absolu du dossier contenant API_Places.py
from API_Places import *
import time

from ConfigurationTest import CustomTestResult

# MARK: - TestGetCityCoordinates
# Classe de test pour la fonction 'get_city_coordinates'
# Vérifie le bon fonctionnement de la fonction qui récupère les coordonnées d'une ville donnée

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


# MARK: - test_valid_city
# Test avec une ville valide (Paris) : Vérifie que la fonction renvoie les bonnes coordonnées
# - Utilise un mock pour simuler une réponse API avec des coordonnées pour Paris
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
                "key": get_api_key(),
                "language": "fr"
            }
        )

# MARK: - test_city_not_found
# Test avec une ville invalide (VilleInexistante) : Vérifie que la fonction retourne None
# - Utilise un mock pour simuler une réponse API vide (aucun résultat trouvé)
    @patch('requests.get')
    def test_city_not_found(self, mock_get):
        # Configuration du mock pour une ville non trouvée
        mock_get.return_value.json.return_value = self.empty_response
        mock_get.return_value.status_code = 200

        # Test avec une ville invalide
        result = get_city_coordinates("VilleInexistante")
        
        # Vérification
        self.assertIsNone(result)

# MARK: - test_api_error
# Test avec une erreur d'API : Vérifie que la fonction gère correctement les erreurs de réseau
# - Simule une exception liée à une erreur de requête API
    @patch('requests.get')
    def test_api_error(self, mock_get):
        # Simulation d'une erreur d'API
        mock_get.side_effect = requests.exceptions.RequestException("Erreur API")

        # Test avec une erreur d'API
        with self.assertRaises(requests.exceptions.RequestException):
            get_city_coordinates("Paris")


# MARK: - test_invalid_response_format
# Test avec une réponse invalide de l'API : Vérifie que la fonction gère bien un format de réponse incorrect
# - Utilise un mock pour simuler une réponse au format invalide (clé manquante dans la réponse)

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