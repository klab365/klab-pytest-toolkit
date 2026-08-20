"""Linux spidev SPI controller implementation for HIL setups."""

from __future__ import annotations

from collections.abc import Callable
from importlib import import_module
from typing import Protocol

from klab_pytest_toolkit_embedded.spi_controllers.interface import SpiController


class SpidevBackend(Protocol):
    def transfer(self, tx_data: bytes) -> bytes: ...
    def close(self) -> None: ...


class SpidevSpiController(SpiController):
    """SPI controller backed by Linux spidev."""

    def __init__(
        self,
        bus: int,
        device: int,
        *,
        max_speed_hz: int = 1_000_000,
        mode: int = 0,
        backend_factory: Callable[[int, int, int, int], SpidevBackend] | None = None,
    ) -> None:
        self._bus = bus
        self._device = device
        self._max_speed_hz = max_speed_hz
        self._mode = mode
        self._backend: SpidevBackend = (backend_factory or _SpidevBackend)(
            bus, device, max_speed_hz, mode
        )

    def transfer(self, tx_data: bytes) -> bytes:
        return self._backend.transfer(tx_data)

    def close(self) -> None:
        self._backend.close()

    def __repr__(self) -> str:
        return (
            f"<SpidevSpiController(bus={self._bus}, device={self._device}, "
            f"max_speed_hz={self._max_speed_hz}, mode={self._mode})>"
        )


class _SpidevBackend:
    """Thin adapter around Linux spidev access."""

    def __init__(self, bus: int, device: int, max_speed_hz: int, mode: int) -> None:
        try:
            SpiDev = import_module("spidev").SpiDev
        except ImportError as exc:
            raise RuntimeError(
                "Linux SPI support requires the optional 'linux' extra " "(installs 'spidev')."
            ) from exc

        self._spi = SpiDev()
        self._spi.open(bus, device)
        self._spi.max_speed_hz = max_speed_hz
        self._spi.mode = mode

    def transfer(self, tx_data: bytes) -> bytes:
        return bytes(self._spi.xfer2(list(tx_data)))

    def close(self) -> None:
        self._spi.close()
