import asyncio
from collections import defaultdict
from contextlib import asynccontextmanager
from typing import Any, Awaitable, Callable, Hashable

from app.core.exceptions import TooManyConcurrentGenerationsError

MAX_CONCURRENT_PER_USER = 2

_in_flight_counts: dict = defaultdict(int)
_pending_calls: dict = {}


@asynccontextmanager
async def user_concurrency_guard(user_id: str):
    """Caps concurrent generations per user, raising past MAX_CONCURRENT_PER_USER."""
    if _in_flight_counts[user_id] >= MAX_CONCURRENT_PER_USER:
        raise TooManyConcurrentGenerationsError()
    _in_flight_counts[user_id] += 1
    try:
        yield
    finally:
        _in_flight_counts[user_id] -= 1
        if _in_flight_counts[user_id] <= 0:
            _in_flight_counts.pop(user_id, None)


async def dedup_call(key: Hashable, coro_factory: Callable[[], Awaitable[Any]]) -> Any:
    """Runs coro_factory() once per key; concurrent calls with the same key share its result.

    A waiter is shielded from the shared future so that cancelling one waiter's
    own task never cancels the future other waiters (or the producer) depend on.
    If the producer itself is cancelled, the future is cancelled too, so waiters
    are woken with CancelledError instead of hanging forever.
    """
    existing = _pending_calls.get(key)
    if existing is not None:
        return await asyncio.shield(existing)

    future = asyncio.get_running_loop().create_future()
    _pending_calls[key] = future
    try:
        result = await coro_factory()
    except asyncio.CancelledError:
        if not future.done():
            future.cancel()
        raise
    except Exception as exc:
        if not future.done():
            future.set_exception(exc)
        raise
    else:
        if not future.done():
            future.set_result(result)
        return result
    finally:
        _pending_calls.pop(key, None)
