"""Connection lifecycle management for Tinkerforge stacks."""

from __future__ import annotations

from collections.abc import Callable
from importlib import import_module
from typing import Protocol


class TinkerforgeConnectionBackend(Protocol):
    """Minimal interface implemented by Tinkerforge's ``IPConnection``."""

    def connect(self, host: str, port: int) -> None: ...
    def disconnect(self) -> None: ...


class TinkerforgeConnection:
    """Own and close one connection to a Tinkerforge ``brickd`` instance.

    Create this object once per test session and pass it to Tinkerforge device
    adapters. ``host`` and ``port`` identify the host running ``brickd``.
    """

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 4223,
        *,
        connection_factory: Callable[[], TinkerforgeConnectionBackend] | None = None,
    ) -> None:
        self._connection = (connection_factory or _ip_connection_factory)()
        self._closed = False
        self._connection.connect(host, port)

    @property
    def client(self) -> TinkerforgeConnectionBackend:
        """Return the underlying ``IPConnection`` for Tinkerforge device bindings."""
        return self._connection

    def close(self) -> None:
        """Disconnect from ``brickd`` once."""
        if not self._closed:
            self._connection.disconnect()
            self._closed = True

    def __enter__(self) -> TinkerforgeConnection:
        """Enter the connection context."""
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        """Close the connection when leaving the context."""
        self.close()


def _ip_connection_factory() -> TinkerforgeConnectionBackend:
    try:
        IPConnection = import_module("tinkerforge.ip_connection").IPConnection
    except ImportError as exc:
        raise RuntimeError(
            "Tinkerforge support requires the optional 'tinkerforge' extra "
            "(installs 'tinkerforge')."
        ) from exc
    return IPConnection()
