"""Linux SMBus/I2C controller implementation for HIL setups."""

from __future__ import annotations

from collections.abc import Callable
from importlib import import_module
from typing import Protocol

from klab_pytest_toolkit_embedded.i2c_controllers.interface import I2cController


class SmbusBackend(Protocol):
    def write(self, address: int, data: bytes) -> None: ...
    def read(self, address: int, count: int) -> bytes: ...
    def close(self) -> None: ...


class SmbusI2cController(I2cController):
    """I2C controller backed by the Linux SMBus interface via smbus2."""

    def __init__(
        self,
        bus: int,
        *,
        backend_factory: Callable[[int], SmbusBackend] | None = None,
    ) -> None:
        self._bus = bus
        self._backend: SmbusBackend = (backend_factory or _SmbusBackend)(bus)

    def write(self, address: int, data: bytes) -> None:
        self._backend.write(address, data)

    def read(self, address: int, count: int) -> bytes:
        return self._backend.read(address, count)

    def close(self) -> None:
        self._backend.close()

    def __repr__(self) -> str:
        return f"<SmbusI2cController(bus={self._bus})>"


class _SmbusBackend:
    """Thin adapter around smbus2 SMBus access."""

    def __init__(self, bus: int) -> None:
        try:
            SMBus = import_module("smbus2").SMBus
        except ImportError as exc:
            raise RuntimeError(
                "Linux SMBus/I2C support requires the optional 'linux' extra "
                "(installs 'smbus2')."
            ) from exc

        self._bus = SMBus(bus)

    def write(self, address: int, data: bytes) -> None:
        self._bus.i2c_rdwr(import_module("smbus2").i2c_msg.write(address, data))

    def read(self, address: int, count: int) -> bytes:
        msg = import_module("smbus2").i2c_msg.read(address, count)
        self._bus.i2c_rdwr(msg)
        return bytes(msg)

    def close(self) -> None:
        self._bus.close()
