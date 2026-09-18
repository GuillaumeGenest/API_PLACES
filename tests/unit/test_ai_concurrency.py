import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import unittest
from app.core.exceptions import TooManyConcurrentGenerationsError
from app.services.ai_concurrency import dedup_call, user_concurrency_guard


class TestUserConcurrencyGuard(unittest.TestCase):

    def test_rejects_beyond_max_concurrent_per_user(self):
        async def hold(user_id, event):
            async with user_concurrency_guard(user_id):
                await event.wait()

        async def run_test():
            event = asyncio.Event()
            t1 = asyncio.create_task(hold("user-1", event))
            t2 = asyncio.create_task(hold("user-1", event))
            await asyncio.sleep(0.01)

            with self.assertRaises(TooManyConcurrentGenerationsError):
                async with user_concurrency_guard("user-1"):
                    pass

            event.set()
            await asyncio.gather(t1, t2)

        asyncio.run(run_test())

    def test_releases_slot_after_use(self):
        async def run_test():
            async with user_concurrency_guard("user-2"):
                pass
            # slot released — this must not raise
            async with user_concurrency_guard("user-2"):
                pass

        asyncio.run(run_test())

    def test_isolated_per_user(self):
        async def hold(user_id, event):
            async with user_concurrency_guard(user_id):
                await event.wait()

        async def run_test():
            event = asyncio.Event()
            t1 = asyncio.create_task(hold("user-3", event))
            t2 = asyncio.create_task(hold("user-3", event))
            await asyncio.sleep(0.01)

            # user-3 is at its cap, but user-4 is unaffected
            async with user_concurrency_guard("user-4"):
                pass

            event.set()
            await asyncio.gather(t1, t2)

        asyncio.run(run_test())


class TestDedupCall(unittest.TestCase):

    def test_concurrent_identical_calls_share_a_single_execution(self):
        call_count = 0

        async def factory():
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.05)
            return "result"

        async def run_test():
            return await asyncio.gather(
                dedup_call("key-1", factory),
                dedup_call("key-1", factory),
            )

        results = asyncio.run(run_test())

        self.assertEqual(call_count, 1)
        self.assertEqual(results, ["result", "result"])

    def test_sequential_calls_each_run_the_factory(self):
        call_count = 0

        async def factory():
            nonlocal call_count
            call_count += 1
            return "result"

        async def run_test():
            await dedup_call("key-2", factory)
            await dedup_call("key-2", factory)

        asyncio.run(run_test())

        self.assertEqual(call_count, 2)

    def test_exception_propagates_to_all_concurrent_waiters(self):
        async def failing_factory():
            await asyncio.sleep(0.01)
            raise ValueError("boom")

        async def run_test():
            return await asyncio.gather(
                dedup_call("key-3", failing_factory),
                dedup_call("key-3", failing_factory),
                return_exceptions=True,
            )

        results = asyncio.run(run_test())

        self.assertEqual(len(results), 2)
        self.assertTrue(all(isinstance(r, ValueError) for r in results))

    def test_producer_cancellation_wakes_other_waiters_instead_of_hanging(self):
        async def slow_factory():
            await asyncio.sleep(1)
            return "unreachable"

        async def run_test():
            producer_task = asyncio.create_task(dedup_call("key-4", slow_factory))
            await asyncio.sleep(0.01)  # producer registers the pending future

            waiter_task = asyncio.create_task(dedup_call("key-4", slow_factory))
            await asyncio.sleep(0.01)  # waiter attaches to the same future

            producer_task.cancel()

            with self.assertRaises(asyncio.CancelledError):
                await producer_task

            # Bounded wait: without the fix, this would hang forever instead
            # of raising CancelledError.
            with self.assertRaises(asyncio.CancelledError):
                await asyncio.wait_for(waiter_task, timeout=1)

        asyncio.run(run_test())

    def test_consumer_cancellation_does_not_affect_shared_future(self):
        call_count = 0

        async def factory():
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.05)
            return "result"

        async def run_test():
            producer_task = asyncio.create_task(dedup_call("key-5", factory))
            await asyncio.sleep(0.01)

            consumer_task = asyncio.create_task(dedup_call("key-5", factory))
            await asyncio.sleep(0.01)

            consumer_task.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await consumer_task

            # The producer and the shared future must be unaffected.
            return await asyncio.wait_for(producer_task, timeout=1)

        result = asyncio.run(run_test())

        self.assertEqual(result, "result")
        self.assertEqual(call_count, 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
