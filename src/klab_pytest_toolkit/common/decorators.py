import functools
import inspect
from collections.abc import Awaitable, Callable

import pytest


def requirement(req_id):
    """Custom decorator to mark a test with a requirement ID and log it in the JUnit report."""

    def decorator(func: Callable) -> Callable[[], Awaitable[None]]:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            if hasattr(pytest, "mark"):
                pytest.mark.requirement(req_id)(func)
            return await func(*args, **kwargs)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            if hasattr(pytest, "mark"):
                pytest.mark.requirement(req_id)(func)
            return func(*args, **kwargs)

        return async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper

    return decorator
