"""Asynchronous BLE GATT client for embedded HIL tests."""

from __future__ import annotations

from collections.abc import Callable
from importlib import import_module
from typing import Protocol


class BleBackend(Protocol):
    """Minimal BLE backend surface used by :class:`BleClient`."""

    async def connect(self) -> None: ...
    async def disconnect(self) -> None: ...
    async def read_gatt_char(self, characteristic: str) -> bytearray: ...
    async def write_gatt_char(self, characteristic: str, data: bytes, response: bool) -> None: ...
    async def start_notify(
        self, characteristic: str, callback: Callable[[bytes], None]
    ) -> None: ...
    async def stop_notify(self, characteristic: str) -> None: ...


class BleClient:
    """Async BLE GATT client backed by the optional :mod:`bleak` package.

    ``BleClient`` intentionally models GATT operations rather than the byte-stream
    communicator interface: reads, writes, and notifications have distinct BLE
    semantics. Set ``pair=True`` to request pairing during connection; the operating
    system handles the pairing prompt and stores any bond.
    """

    def __init__(
        self,
        address: str,
        *,
        pair: bool = False,
        backend_factory: Callable[[str, bool], BleBackend] | None = None,
    ) -> None:
        self._address = address
        self._backend: BleBackend = (backend_factory or _BleakBackend)(address, pair)

    async def connect(self) -> None:
        """Connect to the peripheral."""
        await self._backend.connect()

    async def disconnect(self) -> None:
        """Disconnect from the peripheral."""
        await self._backend.disconnect()

    async def read(self, characteristic: str) -> bytes:
        """Read and return the value of a GATT characteristic."""
        return bytes(await self._backend.read_gatt_char(characteristic))

    async def write(self, characteristic: str, data: bytes, *, response: bool = True) -> None:
        """Write ``data`` to a GATT characteristic."""
        await self._backend.write_gatt_char(characteristic, data, response)

    async def subscribe(self, characteristic: str, callback: Callable[[bytes], None]) -> None:
        """Start forwarding notifications from ``characteristic`` to ``callback``."""
        await self._backend.start_notify(characteristic, callback)

    async def unsubscribe(self, characteristic: str) -> None:
        """Stop notifications from ``characteristic``."""
        await self._backend.stop_notify(characteristic)

    async def __aenter__(self) -> BleClient:
        await self.connect()
        return self

    async def __aexit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        await self.disconnect()

    def __repr__(self) -> str:
        return f"<BleClient(address={self._address!r})>"


class _BleakBackend:
    """Thin adapter around :class:`bleak.BleakClient`."""

    def __init__(self, address: str, pair: bool) -> None:
        try:
            BleakClient = import_module("bleak").BleakClient
        except ImportError as exc:
            raise RuntimeError(
                "BLE support requires the optional 'ble' extra (installs 'bleak')."
            ) from exc
        self._client = BleakClient(address, pair=pair)

    async def connect(self) -> None:
        await self._client.connect()

    async def disconnect(self) -> None:
        await self._client.disconnect()

    async def read_gatt_char(self, characteristic: str) -> bytearray:
        return await self._client.read_gatt_char(characteristic)

    async def write_gatt_char(self, characteristic: str, data: bytes, response: bool) -> None:
        await self._client.write_gatt_char(characteristic, data, response=response)

    async def start_notify(self, characteristic: str, callback: Callable[[bytes], None]) -> None:
        def on_notification(_: object, data: bytearray) -> None:
            callback(bytes(data))

        await self._client.start_notify(characteristic, on_notification)

    async def stop_notify(self, characteristic: str) -> None:
        await self._client.stop_notify(characteristic)
