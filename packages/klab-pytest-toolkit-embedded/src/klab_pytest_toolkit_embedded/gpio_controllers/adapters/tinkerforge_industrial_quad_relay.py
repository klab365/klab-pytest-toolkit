"""Tinkerforge Industrial Quad Relay controller implementation."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from importlib import import_module
from typing import Protocol

from klab_pytest_toolkit_embedded.gpio_controllers.interface import GpioController
from klab_pytest_toolkit_embedded.tinkerforge import TinkerforgeConnection


class _RelayBackend(Protocol):
    def set_value(self, channel: int, value: bool) -> None: ...
    def get_value(self, channel: int) -> bool: ...


@dataclass(frozen=True)
class TinkerforgeRelay:
    """A relay channel on an Industrial Quad Relay Bricklet."""

    channel: int

    def __post_init__(self) -> None:
        if not 0 <= self.channel <= 3:
            raise ValueError("channel must be between 0 and 3")


class TinkerforgeIndustrialQuadRelayController(GpioController):
    """Named relay controller backed by a Tinkerforge Industrial Quad Relay Bricklet."""

    def __init__(
        self,
        connection: TinkerforgeConnection,
        uid: str,
        relays: Mapping[str, TinkerforgeRelay],
        *,
        backend_factory: Callable[[TinkerforgeConnection, str], _RelayBackend] | None = None,
    ) -> None:
        if not relays:
            raise ValueError("relays must contain at least one named relay")
        self._relays = dict(relays)
        self._backend = (backend_factory or _TinkerforgeIndustrialQuadRelayBackend)(connection, uid)

    def write(self, pin: str, value: bool) -> None:
        relay = self._relays[pin]
        self._backend.set_value(relay.channel, value)

    def read(self, pin: str) -> bool:
        relay = self._relays[pin]
        return bool(self._backend.get_value(relay.channel))

    def close(self) -> None:
        """The shared IPConnection owns the physical connection lifecycle."""


class _TinkerforgeIndustrialQuadRelayBackend:
    def __init__(self, connection: TinkerforgeConnection, uid: str) -> None:
        try:
            BrickletIndustrialQuadRelay = import_module(
                "tinkerforge.bricklet_industrial_quad_relay"
            ).BrickletIndustrialQuadRelay
        except ImportError as exc:
            raise RuntimeError(
                "Tinkerforge support requires the optional 'tinkerforge' extra "
                "(installs 'tinkerforge')."
            ) from exc
        self._bricklet = BrickletIndustrialQuadRelay(uid, connection.client)

    def set_value(self, channel: int, value: bool) -> None:
        self._bricklet.set_value(channel, value)

    def get_value(self, channel: int) -> bool:
        return self._bricklet.get_value(channel)
