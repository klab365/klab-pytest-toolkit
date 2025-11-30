import pytest

from klab_pytest_toolkit_decorators import requirement


@requirement("REQ-001")
def test_requirement_decorator_sync():
    """Test that sync functions can be decorated with requirement marker."""
    assert True


@requirement("REQ-002", "REQ-003")
@pytest.mark.asyncio
async def test_requirement_decorator_async_multiple_args():
    """Test that async functions can be decorated with multiple requirement IDs in one call."""
    assert True


@requirement("REQ-004")
@requirement("REQ-005")
def test_multiple_requirement_decorators():
    """Test that multiple requirement decorators can be stacked."""
    assert True


def test_requirement_marker_is_applied():
    """Test that the requirement decorator actually applies the pytest marker."""

    @requirement("REQ-TEST")
    def sample_test():
        pass

    # Check that the marker was applied
    assert hasattr(sample_test, "pytestmark")
    markers = sample_test.pytestmark
    assert len(markers) > 0
    # Find the requirement marker
    req_marker = next((m for m in markers if m.name == "requirement"), None)
    assert req_marker is not None
    assert req_marker.args[0] == "REQ-TEST"


def test_multiple_requirements_via_args():
    """Test that multiple requirements can be passed as arguments."""

    @requirement("REQ-A", "REQ-B", "REQ-C")
    def sample_test():
        pass

    # Check that multiple markers were applied
    assert hasattr(sample_test, "pytestmark")
    markers = sample_test.pytestmark
    req_markers = [m for m in markers if m.name == "requirement"]
    assert len(req_markers) == 3
    req_ids = [m.args[0] for m in req_markers]
    assert "REQ-A" in req_ids
    assert "REQ-B" in req_ids
    assert "REQ-C" in req_ids


def test_multiple_requirements_via_stacking():
    """Test that multiple requirement decorators can be stacked."""

    @requirement("REQ-X")
    @requirement("REQ-Y")
    def sample_test():
        pass

    # Check that multiple markers were applied
    assert hasattr(sample_test, "pytestmark")
    markers = sample_test.pytestmark
    req_markers = [m for m in markers if m.name == "requirement"]
    assert len(req_markers) == 2
    req_ids = [m.args[0] for m in req_markers]
    assert "REQ-X" in req_ids
    assert "REQ-Y" in req_ids


def test_requirement_decorator_requires_id():
    """Test that the requirement decorator requires at least one ID."""
    with pytest.raises(ValueError, match="At least one requirement ID must be provided"):

        @requirement()
        def sample_test():
            pass
