"""FTDI I2C controller implementation for HIL setups."""

from __future__ import annotations

from collections.abc import Callable
from importlib import import_module
from typing import Protocol

from klab_pytest_toolkit_embedded.i2c_controllers.interface import I2cController


class I2cBackend(Protocol):
    def write(self, address: int, data: bytes) -> None: ...
    def read(self, address: int, count: int) -> bytes: ...
    def close(self) -> None: ...


class FtdiI2cController(I2cController):
    """I2C controller backed by an FTDI device via pyftdi."""

    def __init__(
        self,
        url: str,
        *,
        frequency_hz: float = 100_000,
        backend_factory: Callable[[str, float], I2cBackend] | None = None,
    ) -> None:
        self._frequency_hz = frequency_hz
        self._backend: I2cBackend = (backend_factory or _FtdiI2cBackend)(url, frequency_hz)

    def write(self, address: int, data: bytes) -> None:
        self._backend.write(address, data)

    def read(self, address: int, count: int) -> bytes:
        return self._backend.read(address, count)

    def close(self) -> None:
        self._backend.close()

    def __repr__(self) -> str:
        return f"<FtdiI2cController(frequency_hz={self._frequency_hz})>"


class _FtdiI2cBackend:
    """Thin adapter around pyftdi I2C access."""

    def __init__(self, url: str, frequency_hz: float) -> None:
        try:
            PyFtdiI2cController = import_module("pyftdi.i2c").I2cController
        except ImportError as exc:
            raise RuntimeError(
                "FTDI I2C support requires the optional 'ftdi' extra " "(installs 'pyftdi')."
            ) from exc

        self._controller = PyFtdiI2cController()
        self._controller.configure(url, frequency=frequency_hz)

    def write(self, address: int, data: bytes) -> None:
        port = self._controller.get_port(address)
        port.write(data)

    def read(self, address: int, count: int) -> bytes:
        port = self._controller.get_port(address)
        return bytes(port.read(count))

    def close(self) -> None:
        self._controller.close()
