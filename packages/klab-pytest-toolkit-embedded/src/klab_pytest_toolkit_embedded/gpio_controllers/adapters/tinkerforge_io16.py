"""Tinkerforge IO-16 v2 GPIO controller implementation for HIL setups."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from importlib import import_module
from typing import Protocol

from klab_pytest_toolkit_embedded.gpio_controllers.interface import GpioController
from klab_pytest_toolkit_embedded.tinkerforge import TinkerforgeConnection


@dataclass(frozen=True)
class TinkerforgePin:
    """A channel on an IO-16 v2 Bricklet."""

    channel: int

    def __post_init__(self) -> None:
        if not 0 <= self.channel <= 15:
            raise ValueError("channel must be between 0 and 15")


class TinkerforgeIo16Backend(Protocol):
    """Backend interface for an IO-16 v2 Bricklet."""

    def configure_pin(self, pin: TinkerforgePin, output: bool) -> None: ...
    def write_pin(self, pin: TinkerforgePin, value: bool) -> None: ...
    def read_pin(self, pin: TinkerforgePin) -> bool: ...
    def close(self) -> None: ...


class TinkerforgeIO16GpioController(GpioController):
    """Named GPIO controller backed by a Tinkerforge IO-16 v2 Bricklet.

    Named pins are mapped to IO-16 v2 channel numbers (0 through 15). All
    configured pins are outputs by default; pass ``input_pins`` for named pins
    that must be configured as inputs.
    """

    def __init__(
        self,
        connection: TinkerforgeConnection,
        uid: str,
        pins: Mapping[str, TinkerforgePin],
        *,
        input_pins: Iterable[str] = (),
        backend_factory: Callable[[TinkerforgeConnection, str], TinkerforgeIo16Backend]
        | None = None,
    ) -> None:
        if not pins:
            raise ValueError("pins must contain at least one named pin")

        self._pins = dict(pins)
        self._input_pins = frozenset(input_pins)
        unknown_inputs = self._input_pins.difference(self._pins)
        if unknown_inputs:
            raise ValueError(f"input_pins contains unknown pin names: {sorted(unknown_inputs)}")

        self._backend = (backend_factory or _TinkerforgeIO16Backend)(connection, uid)
        for name, pin in self._pins.items():
            self._backend.configure_pin(pin, output=name not in self._input_pins)

    @property
    def pins(self) -> dict[str, TinkerforgePin]:
        """Return the named Tinkerforge pin mapping."""
        return dict(self._pins)

    def pin(self, name: str) -> TinkerforgePin:
        """Resolve a named pin to its Tinkerforge port and index."""
        return self._pins[name]

    def write(self, pin: str, value: bool) -> None:
        if pin in self._input_pins:
            raise ValueError(f"cannot write input pin: {pin}")
        self._backend.write_pin(self.pin(pin), value)

    def read(self, pin: str) -> bool:
        return self._backend.read_pin(self.pin(pin))

    def close(self) -> None:
        """Release the Bricklet adapter; the shared connection remains open."""
        self._backend.close()

    def __repr__(self) -> str:
        return f"<TinkerforgeIO16GpioController(pins={self._pins!r})>"


class _TinkerforgeIO16Backend:
    """Thin adapter around the Tinkerforge IO-16 v2 Python bindings."""

    def __init__(self, connection: TinkerforgeConnection, uid: str) -> None:
        try:
            BrickletIO16V2 = import_module("tinkerforge.bricklet_io16_v2").BrickletIO16V2
        except ImportError as exc:
            raise RuntimeError(
                "Tinkerforge support requires the optional 'tinkerforge' extra "
                "(installs 'tinkerforge')."
            ) from exc
        self._bricklet = BrickletIO16V2(uid, connection.client)

    def configure_pin(self, pin: TinkerforgePin, output: bool) -> None:
        direction = self._bricklet.DIRECTION_OUT if output else self._bricklet.DIRECTION_IN
        self._bricklet.set_configuration(pin.channel, direction, False)

    def write_pin(self, pin: TinkerforgePin, value: bool) -> None:
        self._bricklet.set_selected_value(pin.channel, value)

    def read_pin(self, pin: TinkerforgePin) -> bool:
        return bool(self._bricklet.get_value()[pin.channel])

    def close(self) -> None:
        """The shared IPConnection owns the physical connection lifecycle."""
