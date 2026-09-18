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
    """Runs coro_factory() once per key; concurrent calls with the same key await its result."""
    existing = _pending_calls.get(key)
    if existing is not None:
        return await existing

    future = asyncio.get_running_loop().create_future()
    _pending_calls[key] = future
    try:
        result = await coro_factory()
        future.set_result(result)
    except Exception as exc:
        future.set_exception(exc)
    finally:
        _pending_calls.pop(key, None)
    return await future
