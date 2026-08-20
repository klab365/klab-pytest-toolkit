"""FTDI SPI controller implementation for HIL setups."""

from __future__ import annotations

from collections.abc import Callable
from importlib import import_module
from typing import Protocol

from klab_pytest_toolkit_embedded.spi_controllers.interface import SpiController


class SpiBackend(Protocol):
    def transfer(self, tx_data: bytes) -> bytes: ...
    def close(self) -> None: ...


class FtdiSpiController(SpiController):
    """SPI controller backed by an FTDI device via pyftdi."""

    def __init__(
        self,
        url: str,
        *,
        chip_select: int = 0,
        frequency_hz: float = 1_000_000,
        mode: int = 0,
        backend_factory: Callable[[str, int, float, int], SpiBackend] | None = None,
    ) -> None:
        self._chip_select = chip_select
        self._frequency_hz = frequency_hz
        self._mode = mode
        self._backend: SpiBackend = (backend_factory or _FtdiSpiBackend)(
            url, chip_select, frequency_hz, mode
        )

    def transfer(self, tx_data: bytes) -> bytes:
        return self._backend.transfer(tx_data)

    def close(self) -> None:
        self._backend.close()

    def __repr__(self) -> str:
        return (
            f"<FtdiSpiController(chip_select={self._chip_select}, "
            f"frequency_hz={self._frequency_hz}, mode={self._mode})>"
        )


class _FtdiSpiBackend:
    """Thin adapter around pyftdi SPI access."""

    def __init__(self, url: str, chip_select: int, frequency_hz: float, mode: int) -> None:
        try:
            PyFtdiSpiController = import_module("pyftdi.spi").SpiController
        except ImportError as exc:
            raise RuntimeError(
                "FTDI SPI support requires the optional 'ftdi' extra " "(installs 'pyftdi')."
            ) from exc

        self._controller = PyFtdiSpiController()
        self._controller.configure(url)
        self._port = self._controller.get_port(cs=chip_select, freq=frequency_hz, mode=mode)

    def transfer(self, tx_data: bytes) -> bytes:
        return bytes(self._port.exchange(tx_data, duplex=True))

    def close(self) -> None:
        self._controller.close()
