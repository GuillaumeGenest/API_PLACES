import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from fastapi.testclient import TestClient
from app.main import app


class TestAuthMiddlewareTestingBypass(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app, raise_server_exceptions=False)

    def test_testing_true_avec_environment_production_ne_bypass_pas(self):
        """TESTING=true ne doit jamais bypasser l'auth si ENVIRONMENT=production."""
        original_testing = os.environ.get("TESTING")
        original_environment = os.environ.get("ENVIRONMENT")
        os.environ["TESTING"] = "true"
        os.environ["ENVIRONMENT"] = "production"
        try:
            response = self.client.get("/country_info/NL")
            self.assertEqual(response.status_code, 401)
            self.assertEqual(response.json()["detail"], "Token manquant")
        finally:
            if original_testing is None:
                os.environ.pop("TESTING", None)
            else:
                os.environ["TESTING"] = original_testing
            if original_environment is None:
                os.environ.pop("ENVIRONMENT", None)
            else:
                os.environ["ENVIRONMENT"] = original_environment


if __name__ == '__main__':
    unittest.main(verbosity=2)
