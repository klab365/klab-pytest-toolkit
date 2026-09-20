"""VISA communication implementation for bench instruments."""

from __future__ import annotations

from collections.abc import Callable
from importlib import import_module
from typing import Protocol

from klab_pytest_toolkit_embedded.communicators.interface import CommunicatorInterface


class VisaBackend(Protocol):
    """Minimal VISA resource surface used by :class:`VisaCommunicator`."""

    def write_raw(self, data: bytes) -> None: ...

    def read_bytes(self, count: int) -> bytes: ...

    def read(self) -> str: ...

    def close(self) -> None: ...


class VisaCommunicator(CommunicatorInterface):
    """Communicator backed by a VISA resource (USB, GPIB, TCPIP, ...).

    Requires the optional ``visa`` extra (installs ``pyvisa``).
    """

    def __init__(
        self,
        resource_name: str,
        *,
        backend_factory: Callable[[str], VisaBackend] | None = None,
    ) -> None:
        self._resource_name = resource_name
        self._backend: VisaBackend = (backend_factory or _VisaBackend)(resource_name)

    def send(self, data: bytes) -> None:
        """Send raw bytes to the device."""
        self._backend.write_raw(data)

    def receive(self, num_bytes: int) -> bytes:
        """Receive raw bytes from the device."""
        return self._backend.read_bytes(num_bytes)

    def read_line(self) -> bytes:
        """Read a line using the VISA termination character."""
        return self._backend.read().encode()

    def close(self) -> None:
        """Close the VISA resource."""
        self._backend.close()

    def __enter__(self) -> "VisaCommunicator":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def __repr__(self) -> str:
        return f"<VisaCommunicator(resource={self._resource_name!r})>"


class _VisaBackend:
    """Thin adapter around a pyvisa resource."""

    def __init__(self, resource_name: str) -> None:
        try:
            pyvisa = import_module("pyvisa")
        except ImportError as exc:
            raise RuntimeError(
                "VISA support requires the optional 'visa' extra (installs 'pyvisa')."
            ) from exc

        self._resource = pyvisa.ResourceManager().open_resource(resource_name)
        self._resource.read_termination = "\n"
        self._resource.write_termination = "\n"

    def write_raw(self, data: bytes) -> None:
        self._resource.write_raw(data)

    def read_bytes(self, count: int) -> bytes:
        return self._resource.read_bytes(count)

    def read(self) -> str:
        return self._resource.read()

    def close(self) -> None:
        self._resource.close()
