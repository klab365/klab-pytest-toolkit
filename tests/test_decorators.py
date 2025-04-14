from unittest.mock import patch
import pytest

from klab_pytest_toolkit.common.decorators import requirement

def test_requirement_decorator_sync():
    @requirement(456)
    def sync_test_func():
        pass
    
    with patch('pytest.mark.requirement') as mock_requirement:
        sync_test_func()
        assert mock_requirement.called
        call_args = mock_requirement.call_args[0][0]
        assert call_args == 456

def test_requirement_decorator_async():
    @pytest.mark.asyncio
    @requirement(789)
    async def async_test_func():
        pass
    
    with patch('pytest.mark.requirement') as mock_requirement:
        async_test_func()
        assert mock_requirement.called
        call_args = mock_requirement.call_args[0][0]
        assert call_args == 789
