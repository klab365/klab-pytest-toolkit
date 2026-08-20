"""FTDI GPIO controller implementation for HIL setups."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from importlib import import_module
from typing import Protocol

from klab_pytest_toolkit_embedded.gpio_controllers.interface import GpioController


class GpioBackend(Protocol):
    def write_pin(self, bit: int, value: bool) -> None: ...
    def read_pin(self, bit: int) -> bool: ...
    def close(self) -> None: ...


class FtdiGpioController(GpioController):
    """GPIO controller backed by an FTDI device via pyftdi."""

    def __init__(
        self,
        url: str,
        pins: Mapping[str, int],
        *,
        direction: int | None = None,
        backend_factory: Callable[[str, int], GpioBackend] | None = None,
    ) -> None:
        if not pins:
            raise ValueError("pins must contain at least one named pin")

        self._pins = dict(pins)
        self._direction = (
            direction if direction is not None else self._direction_mask(self._pins.values())
        )
        self._backend: GpioBackend = (backend_factory or _FtdiGpioBackend)(url, self._direction)

    @property
    def pins(self) -> dict[str, int]:
        """Return the named pin mapping."""
        return dict(self._pins)

    def pin(self, name: str) -> int:
        """Resolve a named pin to its FTDI bit index."""
        return self._pins[name]

    def write(self, pin: str, value: bool) -> None:
        self._backend.write_pin(self.pin(pin), value)

    def read(self, pin: str) -> bool:
        return self._backend.read_pin(self.pin(pin))

    def close(self) -> None:
        self._backend.close()

    @staticmethod
    def _direction_mask(pins: Iterable[int]) -> int:
        mask = 0
        for bit in pins:
            mask |= 1 << int(bit)
        return mask

    def __repr__(self) -> str:
        return f"<FtdiGpioController(pins={self._pins!r})>"


class _FtdiGpioBackend:
    """Thin adapter around pyftdi GPIO access."""

    def __init__(self, url: str, direction: int) -> None:
        try:
            GpioAsyncController = import_module("pyftdi.gpio").GpioAsyncController
        except ImportError as exc:
            raise RuntimeError(
                "FTDI GPIO support requires the optional 'ftdi' extra " "(installs 'pyftdi')."
            ) from exc

        self._controller = GpioAsyncController()
        self._controller.configure(url, direction=direction)
        self._state = 0

    def write_pin(self, bit: int, value: bool) -> None:
        if value:
            self._state |= 1 << bit
        else:
            self._state &= ~(1 << bit)
        self._controller.write(self._state)

    def read_pin(self, bit: int) -> bool:
        return bool(self._controller.read() & (1 << bit))

    def close(self) -> None:
        self._controller.close()
