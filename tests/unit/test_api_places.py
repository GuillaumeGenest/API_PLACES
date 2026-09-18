import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import threading
import time
import unittest
from unittest.mock import patch
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


if __name__ == '__main__':
    unittest.main(verbosity=2)
