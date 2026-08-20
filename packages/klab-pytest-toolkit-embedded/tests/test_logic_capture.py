"""Unit tests for the LogicCapture interface."""

import pytest

from klab_pytest_toolkit_embedded.logic_analyzers import LogicCapture


class MockLogicCapture(LogicCapture):
    """Mock logic capture implementation for testing."""

    def __init__(self) -> None:
        self._digital_channels = {"clk": 0, "mosi": 1, "idle": 2}
        self._transitions = {"clk": [0.1, 0.2, 0.3], "mosi": [0.15], "idle": []}
        self.exported_path: str | None = None

    @property
    def digital_channels(self):
        return dict(self._digital_channels)

    def channel(self, name: str) -> int:
        return self._digital_channels[name]

    def transitions(self, name: str):
        return list(self._transitions[name])

    def export(self, path: str) -> None:
        self.exported_path = path


def test_logic_capture_exposes_named_channels() -> None:
    capture = MockLogicCapture()

    assert capture.digital_channels == {"clk": 0, "mosi": 1, "idle": 2}
    assert capture.channel("clk") == 0


def test_logic_capture_can_export() -> None:
    capture = MockLogicCapture()

    capture.export("capture.sal")

    assert capture.exported_path == "capture.sal"


def test_logic_capture_base_assertions() -> None:
    capture = MockLogicCapture()

    assert capture.has_channel("clk") is True
    capture.assert_has_channel("clk")
    capture.assert_has_channels("clk", "mosi")
    capture.assert_any_activity("clk")
    capture.assert_no_activity("idle")
    capture.assert_toggles_at_least("clk", 3)


def test_logic_capture_assertions_fail_with_clear_messages() -> None:
    capture = MockLogicCapture()

    with pytest.raises(AssertionError, match="not found"):
        capture.assert_has_channel("missing")

    with pytest.raises(AssertionError, match="no activity"):
        capture.assert_no_activity("mosi")

    with pytest.raises(AssertionError, match="at least 2 times, got 1"):
        capture.assert_toggles_at_least("mosi", 2)
