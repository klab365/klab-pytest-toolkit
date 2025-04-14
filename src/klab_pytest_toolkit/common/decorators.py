import functools
import inspect
import pytest


def requirement(req_id):
    """Custom decorator to mark a test with a requirement ID and log it in the JUnit report."""
    def decorator(func):
        REQUIREMENT_LABEL = "requirement"

        @pytest.mark.requirement(req_id)
        @functools.wraps(func)
        async def async_wrapper(*args, request, **kwargs):
            request.node.user_properties.append((REQUIREMENT_LABEL, req_id))
            return await func(*args, request=request, **kwargs)

        @pytest.mark.requirement(req_id)
        @functools.wraps(func)
        def sync_wrapper(*args, request, **kwargs):
            request.node.user_properties.append((REQUIREMENT_LABEL, req_id))
            return func(*args, request=request, **kwargs)

        return async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper
    return decorator
