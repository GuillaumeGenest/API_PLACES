import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import threading
import time
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import auth_middleware


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


class TestAuthMiddlewareConcurrency(unittest.TestCase):

    def test_jwks_lookup_does_not_block_event_loop(self):
        original_testing = os.environ.get("TESTING")
        original_environment = os.environ.get("ENVIRONMENT")
        os.environ["TESTING"] = "true"
        os.environ["ENVIRONMENT"] = "production"
        try:
            started = threading.Event()
            release = threading.Event()

            class FakeKey:
                key = "not-a-real-key"

            def fake_get_signing_key_from_jwt(token):
                started.set()
                release.wait(timeout=2)
                return FakeKey()

            class FakeURL:
                path = "/attractions/"

            class FakeState:
                pass

            class FakeRequest:
                def __init__(self):
                    self.url = FakeURL()
                    self.headers = {"Authorization": "Bearer faketoken"}
                    self.state = FakeState()

            async def call_next(request):
                return "OK"

            async def witness():
                while not started.is_set():
                    await asyncio.sleep(0.01)
                release.set()

            async def run_test():
                with patch(
                    'app.core.security.jwks_client.get_signing_key_from_jwt',
                    side_effect=fake_get_signing_key_from_jwt,
                ):
                    start = time.monotonic()
                    await asyncio.gather(
                        auth_middleware(FakeRequest(), call_next),
                        witness(),
                    )
                    return time.monotonic() - start

            elapsed = asyncio.run(run_test())
            self.assertLess(elapsed, 1.0)
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
