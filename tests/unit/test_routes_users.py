import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import threading
import time
import unittest
from unittest.mock import patch
from app.routers.users import delete_me


class TestDeleteMeConcurrency(unittest.TestCase):

    def test_delete_me_does_not_block_event_loop(self):
        started = threading.Event()
        release = threading.Event()

        def fake_delete_user(user_id):
            started.set()
            release.wait(timeout=2)
            return True

        async def witness():
            while not started.is_set():
                await asyncio.sleep(0.01)
            release.set()

        async def run_test():
            with patch(
                'app.routers.users.delete_user',
                side_effect=fake_delete_user,
            ):
                start = time.monotonic()
                result, _ = await asyncio.gather(
                    delete_me(user={"sub": "test-user-id"}),
                    witness(),
                )
                elapsed = time.monotonic() - start
                return result, elapsed

        result, elapsed = asyncio.run(run_test())

        self.assertLess(elapsed, 1.0)
        self.assertEqual(result, {"status": "success", "user_id": "test-user-id"})


if __name__ == '__main__':
    unittest.main(verbosity=2)
