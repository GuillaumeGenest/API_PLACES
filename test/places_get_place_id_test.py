# import unittest
# from unittest.mock import patch, Mock
# import sys
# import os
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# # Définir l'environnement de test avant d'importer les modules
# os.environ['ENVIRONMENT'] = 'testing'
# from API_Places import *
# import time

# from ConfigurationTest import CustomTestResult

# ###############################################################
# #               test unitaire 
# ###############################################################

# # Classe personnalisée pour afficher les informations supplémentaires

# class TestGetPlaceID(unittest.TestCase):

# # MARK: - test_get_place_id_success
# # Test réussi pour la récupération du place_id lorsque le lieu existe.
# # - Utilise un mock pour simuler une réponse API réussie avec un lieu valide
#     @patch('requests.get')
#     def test_get_place_id_success(self, mock_get):
#         # Arrange
#         mock_response = Mock()
#         mock_response.json.return_value = {
#             'candidates': [{'place_id': 'ChIJN1t_tDeuEmsRUcIaDl2FZ5I'}],
#             'status': 'OK'
#         }
#         mock_get.return_value = mock_response
#         location = "Sydney, Australia"

#         # Act
#         result = get_place_id(location)

#         # Assert
#         self.assertEqual(result, 'ChIJN1t_tDeuEmsRUcIaDl2FZ5I')
#         mock_get.assert_called_once_with(
#             "https://maps.googleapis.com/maps/api/place/findplacefromtext/json",
#             params={
#                 "input": location,
#                 "inputtype": "textquery",
#                 "key": GOOGLE_API_KEY
#             }
#         )

# # MARK: - test_get_place_id_no_results
# # Test lorsque aucun résultat n'est trouvé pour le lieu fourni.
# # - Utilise un mock pour simuler une réponse indiquant qu'il n'y a pas de résultat pour le lieu.
#     @patch('requests.get')
#     def test_get_place_id_no_results(self, mock_get):
#          # Arrange
#         mock_response = Mock()
#         mock_response.json.return_value = {
#              'candidates': [],
#              'status': 'ZERO_RESULTS'
#         }
#         mock_get.return_value = mock_response
#         location = "NonExistentPlace"

#          # Act
#         result = get_place_id(location)

#          # Assert
#         self.assertIsNone(result)
#         mock_get.assert_called_once()


# # MARK: - test_get_place_id_api_error
# # Test lorsque l'API retourne une erreur (exemple : clé API invalide).
# # - Simule une réponse d'erreur avec un statut 'REQUEST_DENIED' et sans 'candidates'
#     @patch('requests.get')
#     def test_get_place_id_api_error(self, mock_get):
#     #     # Arrange : Simuler une réponse d'erreur avec un statut 'REQUEST_DENIED' et sans 'candidates'
#         mock_response = Mock()
#         mock_response.json.return_value = {
#             'status': 'REQUEST_DENIED',
#             'error_message': 'Invalid API key'
#         }
#         mock_get.return_value = mock_response
#         location = "Paris, France"

#     #     # Act : Appel à la fonction
#         result = get_place_id(location)

#     #     # Assert : Vérification que None est retourné et que la clé 'candidates' n'est pas dans la réponse
#         self.assertIsNone(result)
#         mock_get.assert_called_once()


# if __name__ == '__main__':

#     print("###############################################################")
#     print("Lancement des tests unitaires -------   get_place_id   --------")                
#     print("###############################################################")

#     # Création du test runner personnalisé
#     runner = unittest.TextTestRunner(resultclass=CustomTestResult)
#     unittest.main(testRunner=runner, verbosity=2)