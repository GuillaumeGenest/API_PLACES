import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import threading
import time
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from app.api.API_Places import get_tourist_attraction


class TestGetTouristAttractionConcurrency(unittest.TestCase):

    def test_cache_hit_supabase_call_does_not_block_event_loop(self):
        started = threading.Event()
        release = threading.Event()

        def fake_get_attraction_by_place_id(place_id):
            started.set()
            release.wait(timeout=2)
            return {"place_id": place_id}

        async def witness():
            while not started.is_set():
                await asyncio.sleep(0.01)
            release.set()

        async def run_test():
            with patch(
                'app.api.API_Places.get_attraction_by_place_id',
                side_effect=fake_get_attraction_by_place_id,
            ):
                start = time.monotonic()
                result, _ = await asyncio.gather(
                    get_tourist_attraction("ChIJD7fiBh9u5kcRYJSMaMOCCwQ"),
                    witness(),
                )
                elapsed = time.monotonic() - start
                return result, elapsed

        result, elapsed = asyncio.run(run_test())

        self.assertLess(elapsed, 1.0)
        self.assertEqual(
            result,
            {"attraction": {"place_id": "ChIJD7fiBh9u5kcRYJSMaMOCCwQ"}},
        )


class TestGetTouristAttractionCacheMiss(unittest.TestCase):

    def test_cache_miss_routes_description_through_ai_service(self):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json = MagicMock(return_value={
            "id": "ChIJD7fiBh9u5kcRYJSMaMOCCwQ",
            "displayName": {"text": "Tour Eiffel"},
            "formattedAddress": "Paris",
        })

        mock_async_client = MagicMock()
        mock_async_client.__aenter__ = AsyncMock(return_value=mock_async_client)
        mock_async_client.__aexit__ = AsyncMock(return_value=False)
        mock_async_client.get = AsyncMock(return_value=mock_response)

        async def run_test():
            with patch('app.api.API_Places.get_attraction_by_place_id', return_value=None), \
                    patch('app.api.API_Places.httpx.AsyncClient', return_value=mock_async_client), \
                    patch('app.api.API_Places.AIService') as MockAIService, \
                    patch('app.api.API_Places.is_stored', return_value=True), \
                    patch('app.api.API_Places.get_storage_url', return_value='http://example.com/photo.jpg'), \
                    patch('app.api.API_Places.save_attraction', return_value=True):
                ai_instance = MockAIService.return_value
                ai_instance.generate_description = AsyncMock(return_value="Une description.")

                result = await get_tourist_attraction("ChIJD7fiBh9u5kcRYJSMaMOCCwQ", user_id="user-42")

                ai_instance.generate_description.assert_called_once_with(
                    "Tour Eiffel", "Paris", user_id="user-42"
                )
                return result

        result = asyncio.run(run_test())

        self.assertEqual(result["attraction"]["description"], "Une description.")


if __name__ == '__main__':
    unittest.main(verbosity=2)
