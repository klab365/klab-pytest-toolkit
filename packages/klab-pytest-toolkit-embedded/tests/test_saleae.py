"""Unit tests for the SaleaeLogicAnalyzer class."""

from pathlib import Path
from typing import cast

import pytest

from klab_pytest_toolkit_embedded.logic_analyzers import SaleaeLogicAnalyzer


class MockSaleaeBackend:
    """Mock backend for SaleaeLogicAnalyzer tests."""

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.started_with = None
        self.stopped = False
        self.exported_path = None
        self.exported_channels = None
        self.closed = False

    def start_capture(self, *, digital_channels, sample_rate_hz, capture_seconds) -> None:
        self.started_with = {
            "digital_channels": digital_channels,
            "sample_rate_hz": sample_rate_hz,
            "capture_seconds": capture_seconds,
        }

    def stop_capture(self) -> None:
        self.stopped = True

    def export(self, path: Path, *, digital_channels) -> None:
        self.exported_path = path
        self.exported_channels = dict(digital_channels)

    def close(self) -> None:
        self.closed = True


def test_saleae_accepts_named_channels() -> None:
    analyzer = SaleaeLogicAnalyzer(
        digital_channels={"mosi": 0, "miso": 1, "clk": 2},
        sample_rate_hz=25_000_000,
        backend_factory=MockSaleaeBackend,
    )

    assert analyzer.channel("mosi") == 0
    assert analyzer.channel("miso") == 1
    assert analyzer.digital_channels == {"mosi": 0, "miso": 1, "clk": 2}


def test_saleae_start_stop_and_export() -> None:
    analyzer = SaleaeLogicAnalyzer(
        digital_channels={"reset": 0, "boot": 1},
        sample_rate_hz=10_000_000,
        capture_seconds=2.5,
        host="saleae.local",
        port=9999,
        backend_factory=MockSaleaeBackend,
    )

    analyzer.start_capture()
    analyzer.stop_capture()
    analyzer.export("artifacts/capture.sal")

    backend = cast(MockSaleaeBackend, analyzer._backend)
    assert backend.host == "saleae.local"
    assert backend.port == 9999
    assert backend.started_with == {
        "digital_channels": [0, 1],
        "sample_rate_hz": 10_000_000,
        "capture_seconds": 2.5,
    }
    assert backend.stopped is True
    assert backend.exported_path == Path("artifacts/capture.sal")
    assert backend.exported_channels == {"reset": 0, "boot": 1}


def test_saleae_get_capture_returns_named_capture() -> None:
    analyzer = SaleaeLogicAnalyzer(
        digital_channels={"reset": 0, "boot": 1},
        sample_rate_hz=10_000_000,
        backend_factory=MockSaleaeBackend,
    )

    analyzer.start_capture()
    capture = analyzer.get_capture()

    assert capture.digital_channels == {"reset": 0, "boot": 1}
    assert capture.channel("boot") == 1


def test_saleae_capture_transitions_not_implemented_yet() -> None:
    analyzer = SaleaeLogicAnalyzer(
        digital_channels={"reset": 0},
        sample_rate_hz=10_000_000,
        backend_factory=MockSaleaeBackend,
    )

    analyzer.start_capture()
    capture = analyzer.get_capture()

    with pytest.raises(NotImplementedError, match="transition analysis"):
        capture.transitions("reset")


def test_saleae_requires_named_channels() -> None:
    with pytest.raises(ValueError, match="digital_channels"):
        SaleaeLogicAnalyzer(
            digital_channels={},
            sample_rate_hz=1_000_000,
            backend_factory=MockSaleaeBackend,
        )


def test_saleae_raises_when_capture_not_started() -> None:
    analyzer = SaleaeLogicAnalyzer(
        digital_channels={"clk": 0},
        sample_rate_hz=1_000_000,
        backend_factory=MockSaleaeBackend,
    )

    with pytest.raises(RuntimeError, match="No Saleae capture"):
        analyzer.get_capture()


def test_saleae_context_manager_closes_backend() -> None:
    analyzer = SaleaeLogicAnalyzer(
        digital_channels={"clk": 0},
        sample_rate_hz=1_000_000,
        backend_factory=MockSaleaeBackend,
    )

    with analyzer as active_analyzer:
        assert active_analyzer is analyzer

    backend = cast(MockSaleaeBackend, analyzer._backend)
    assert backend.closed is True
