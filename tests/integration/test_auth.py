import os
import httpx
import unittest
from fastapi.testclient import TestClient
from app.main import app


def get_supabase_token() -> str:
    """Récupère un vrai token Supabase"""
    response = httpx.post(
        f"{os.getenv('SUPABASE_BASE_URL_DEV')}/auth/v1/token?grant_type=password",
        headers={
            "apikey": os.getenv("SUPABASE_API_KEY_DEV"),
            "Content-Type": "application/json"
        },
        json={
            "email": os.getenv("TEST_USER_EMAIL"),
            "password": os.getenv("TEST_USER_PASSWORD")
        }
    )
    return response.json()["access_token"]


class TestAuthMiddleware(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app, raise_server_exceptions=False)

    def test_sans_token_retourne_401(self):
        response = self.client.get("/country_info/NL")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Token manquant")

    def test_faux_token_retourne_401(self):
        response = self.client.get(
            "/country_info/NL",
            headers={"Authorization": "Bearer tokenbidon"}
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Token invalide")

    def test_vrai_token_retourne_200(self):
        token = get_supabase_token()
        response = self.client.get(
            "/country_info/NL",
            headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main(verbosity=2)