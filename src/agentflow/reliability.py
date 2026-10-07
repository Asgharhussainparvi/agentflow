import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar

T = TypeVar("T")


async def retry_async(
    operation: Callable[[], Awaitable[T]],
    retries: int = 3,
    base_delay: float = 0.5,
) -> T:
    """
    Execute an async operation with exponential backoff.

    Example delays:
        0.5s -> 1.0s -> 2.0s
    """

    last_error: Exception | None = None

    for attempt in range(retries + 1):
        try:
            return await operation()

        except Exception as exc:
            last_error = exc

            if attempt >= retries:
                raise

            delay = base_delay * (2**attempt)
            await asyncio.sleep(delay)

    # Defensive fallback; normally unreachable.
    assert last_error is not None
    raise last_error
