import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app


def make_country(name="France", country_code="FR"):
    country = MagicMock()
    country.id = 1
    country.name = name
    country.country_code = country_code
    country.capital = "Paris"
    country.population = 67000000
    country.currency = "Euro"
    country.currency_symbol = "€"
    country.phone_code = "+33"
    country.utc_offset = 1
    country.visa = "Visa not required for EU citizens"
    country.climate = "Temperate"
    country.religion = "Christianity"
    country.culinary_customs = ["Bread with every meal", "Long lunches"]
    country.social_customs = ["Greet with a kiss on the cheek"]
    country.politeness_phrases = {"hello": "Bonjour", "thank you": "Merci"}
    country.basic_vocabulary = {"yes": "Oui", "no": "Non"}
    country.numbers = {"1": "un", "2": "deux"}
    country.emergency_numbers = {"police": "17", "fire": "18"}
    return country


class TestListCountries(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_list_countries_success(self):
        countries = [make_country("France", "FR"), make_country("Germany", "DE")]
        with patch('app.routers.countries_info.get_all_countries', return_value=countries):
            response = self.client.get("/country_info/")
            self.assertEqual(response.status_code, 200)

    def test_list_countries_not_found(self):
        with patch('app.routers.countries_info.get_all_countries', return_value=None):
            response = self.client.get("/country_info/")
            self.assertEqual(response.status_code, 404)
            self.assertIn("Aucun pays trouvé", response.json()["detail"])

    def test_list_countries_empty(self):
        with patch('app.routers.countries_info.get_all_countries', return_value=[]):
            response = self.client.get("/country_info/")
            self.assertEqual(response.status_code, 404)
            self.assertIn("Aucun pays trouvé", response.json()["detail"])


class TestSearchCountries(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_search_success(self):
        countries = [make_country("France", "FR")]
        with patch('app.routers.countries_info.search_countries', return_value=countries):
            response = self.client.get("/country_info/search?query=France")
            self.assertEqual(response.status_code, 200)

    def test_search_not_found(self):
        with patch('app.routers.countries_info.search_countries', return_value=None):
            response = self.client.get("/country_info/search?query=Inconnu")
            self.assertEqual(response.status_code, 404)
            self.assertIn("Aucun pays trouvé pour", response.json()["detail"])

    def test_search_empty_results(self):
        with patch('app.routers.countries_info.search_countries', return_value=[]):
            response = self.client.get("/country_info/search?query=Inconnu")
            self.assertEqual(response.status_code, 404)
            self.assertIn("Aucun pays trouvé pour", response.json()["detail"])

    def test_search_missing_query(self):
        response = self.client.get("/country_info/search")
        self.assertEqual(response.status_code, 422)


class TestGetCountryByCode(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_get_country_success(self):
        country = make_country("France", "FR")
        with patch('app.routers.countries_info.get_country_by_code', return_value=country):
            response = self.client.get("/country_info/FR")
            self.assertEqual(response.status_code, 200)

    def test_get_country_not_found(self):
        with patch('app.routers.countries_info.get_country_by_code', return_value=None):
            response = self.client.get("/country_info/XX")
            self.assertEqual(response.status_code, 404)
            self.assertIn("Pays introuvable", response.json()["detail"])


if __name__ == '__main__':
    unittest.main(verbosity=2)