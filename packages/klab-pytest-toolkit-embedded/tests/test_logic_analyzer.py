"""Unit tests for the LogicAnalyzer interface."""

from klab_pytest_toolkit_embedded.logic_analyzers import LogicAnalyzer, LogicCapture


class MockLogicCapture(LogicCapture):
    def __init__(self) -> None:
        self._digital_channels = {"clk": 0}
        self.exported_path: str | None = None

    @property
    def digital_channels(self):
        return dict(self._digital_channels)

    def channel(self, name: str) -> int:
        return self._digital_channels[name]

    def transitions(self, name: str):
        return [0.1]

    def export(self, path: str) -> None:
        self.exported_path = path


class MockLogicAnalyzer(LogicAnalyzer):
    """Mock logic analyzer implementation for testing."""

    def __init__(self) -> None:
        self.started = False
        self.stopped = False
        self.closed = False
        self.exported_path: str | None = None
        self.capture = MockLogicCapture()

    def start_capture(self) -> None:
        self.started = True

    def stop_capture(self) -> None:
        self.stopped = True

    def export(self, path: str) -> None:
        self.exported_path = path

    def get_capture(self) -> LogicCapture:
        return self.capture

    def close(self) -> None:
        self.closed = True


def test_logic_analyzer_can_start_stop_and_export() -> None:
    analyzer = MockLogicAnalyzer()

    analyzer.start_capture()
    analyzer.stop_capture()
    analyzer.export("capture.sal")

    assert analyzer.started is True
    assert analyzer.stopped is True
    assert analyzer.exported_path == "capture.sal"


def test_logic_analyzer_exposes_capture() -> None:
    analyzer = MockLogicAnalyzer()

    capture = analyzer.get_capture()

    assert capture.channel("clk") == 0


def test_logic_analyzer_context_manager_closes() -> None:
    analyzer = MockLogicAnalyzer()

    with analyzer as active_analyzer:
        assert active_analyzer is analyzer

    assert analyzer.closed is True
