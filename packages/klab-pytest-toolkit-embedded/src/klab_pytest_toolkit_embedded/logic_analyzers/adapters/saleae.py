"""Saleae logic analyzer implementation for HIL setups."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from importlib import import_module
from pathlib import Path
from typing import Protocol

from klab_pytest_toolkit_embedded.logic_analyzers.capture import LogicCapture
from klab_pytest_toolkit_embedded.logic_analyzers.interface import LogicAnalyzer


class SaleaeBackend(Protocol):
    def start_capture(
        self,
        *,
        digital_channels: Sequence[int],
        sample_rate_hz: int,
        capture_seconds: float | None,
    ) -> None: ...
    def stop_capture(self) -> None: ...
    def export(self, path: Path, *, digital_channels: Mapping[str, int]) -> None: ...
    def close(self) -> None: ...


class SaleaeLogicAnalyzer(LogicAnalyzer):
    """Logic analyzer implementation backed by the Saleae Automation API.

    Channel names are provided by the user and mapped to Saleae digital channel
    indices, for example ``{"spi_mosi": 0, "spi_miso": 1, "spi_clk": 2}``.
    """

    def __init__(
        self,
        digital_channels: Mapping[str, int],
        *,
        sample_rate_hz: int,
        capture_seconds: float | None = None,
        host: str = "127.0.0.1",
        port: int = 10430,
        backend_factory: Callable[[str, int], SaleaeBackend] | None = None,
    ) -> None:
        if not digital_channels:
            raise ValueError("digital_channels must contain at least one named channel")

        self._digital_channels = dict(digital_channels)
        self._sample_rate_hz = sample_rate_hz
        self._capture_seconds = capture_seconds
        self._backend: SaleaeBackend = (backend_factory or _SaleaeAutomationBackend)(host, port)
        self._capture: SaleaeLogicCapture | None = None

    @property
    def digital_channels(self) -> dict[str, int]:
        """Return the named digital channel mapping."""
        return dict(self._digital_channels)

    def channel(self, name: str) -> int:
        """Resolve a named channel to its Saleae channel index."""
        return self._digital_channels[name]

    def start_capture(self) -> None:
        """Start a Saleae capture session."""
        self._backend.start_capture(
            digital_channels=list(self._digital_channels.values()),
            sample_rate_hz=self._sample_rate_hz,
            capture_seconds=self._capture_seconds,
        )
        self._capture = SaleaeLogicCapture(self._backend, self._digital_channels)

    def stop_capture(self) -> None:
        """Stop the current Saleae capture session."""
        self._backend.stop_capture()

    def export(self, path: str) -> None:
        """Export the current capture.

        Native Saleae session files should usually use the ``.sal`` extension.
        """
        self.get_capture().export(path)

    def get_capture(self) -> LogicCapture:
        """Return the current Saleae capture wrapper."""
        if self._capture is None:
            raise RuntimeError("No Saleae capture available")
        return self._capture

    def close(self) -> None:
        """Close the logic analyzer connection."""
        self._capture = None
        self._backend.close()

    def __repr__(self) -> str:
        return (
            f"<SaleaeLogicAnalyzer(digital_channels={self._digital_channels!r}, "
            f"sample_rate_hz={self._sample_rate_hz})>"
        )


class SaleaeLogicCapture(LogicCapture):
    """Captured Saleae session with named digital channels."""

    def __init__(self, backend: SaleaeBackend, digital_channels: Mapping[str, int]) -> None:
        self._backend = backend
        self._digital_channels = dict(digital_channels)

    @property
    def digital_channels(self) -> dict[str, int]:
        return dict(self._digital_channels)

    def channel(self, name: str) -> int:
        return self._digital_channels[name]

    def transitions(self, name: str) -> Sequence[float]:
        self.assert_has_channel(name)
        raise NotImplementedError(
            "Saleae transition analysis is not implemented yet. Export the capture or add a decoded-data backend."
        )

    def export(self, path: str) -> None:
        self._backend.export(Path(path), digital_channels=self._digital_channels)


class _SaleaeAutomationBackend:
    """Thin adapter around the Saleae Automation API."""

    def __init__(self, host: str, port: int) -> None:
        try:
            automation = import_module("saleae.automation")
        except ImportError as exc:
            raise RuntimeError(
                "Saleae automation support requires the optional 'saleae' extra "
                "(installs 'logic2-automation') and a running Saleae Logic application "
                "with the automation server enabled."
            ) from exc

        self._automation = automation
        self._manager = automation.Manager.connect(host=host, port=port)
        self._capture = None

    def start_capture(
        self,
        *,
        digital_channels: Sequence[int],
        sample_rate_hz: int,
        capture_seconds: float | None,
    ) -> None:
        capture_mode = (
            self._automation.TimedCaptureMode(capture_seconds)
            if capture_seconds is not None
            else self._automation.ManualCaptureMode()
        )
        device_configuration = self._automation.LogicDeviceConfiguration(
            enabled_digital_channels=list(digital_channels),
            digital_sample_rate=sample_rate_hz,
        )
        capture_configuration = self._automation.CaptureConfiguration(capture_mode=capture_mode)
        self._capture = self._manager.start_capture(
            device_id=None,
            device_configuration=device_configuration,
            capture_configuration=capture_configuration,
        )

    def stop_capture(self) -> None:
        if self._capture is None:
            raise RuntimeError("No active Saleae capture")
        self._capture.stop()

    def export(self, path: Path, *, digital_channels: Mapping[str, int]) -> None:
        if self._capture is None:
            raise RuntimeError("No Saleae capture available for export")
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix == ".sal":
            self._capture.save_capture(path)
            return
        raise ValueError("Only native Saleae .sal export is currently supported")

    def close(self) -> None:
        self._capture = None
