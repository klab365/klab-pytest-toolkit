"""Tests for the BLE GATT client."""

from collections.abc import Callable
from unittest.mock import patch

import pytest

from klab_pytest_toolkit_embedded.ble import BleClient


class FakeBleBackend:
    """In-memory BLE backend for deterministic client tests."""

    def __init__(self, address: str) -> None:
        self.address = address
        self.connected = False
        self.read_values = {"read-char": bytearray(b"value")}
        self.writes: list[tuple[str, bytes, bool]] = []
        self.callbacks: dict[str, Callable[[bytes], None]] = {}

    async def connect(self) -> None:
        self.connected = True

    async def disconnect(self) -> None:
        self.connected = False

    async def read_gatt_char(self, characteristic: str) -> bytearray:
        return self.read_values[characteristic]

    async def write_gatt_char(self, characteristic: str, data: bytes, response: bool) -> None:
        self.writes.append((characteristic, data, response))

    async def start_notify(self, characteristic: str, callback: Callable[[bytes], None]) -> None:
        self.callbacks[characteristic] = callback

    async def stop_notify(self, characteristic: str) -> None:
        del self.callbacks[characteristic]


def make_client() -> tuple[BleClient, FakeBleBackend]:
    backend = FakeBleBackend("AA:BB:CC:DD:EE:FF")
    client = BleClient(backend.address, backend_factory=lambda _, __: backend)
    return client, backend


@pytest.mark.asyncio
async def test_connect_and_disconnect() -> None:
    client, backend = make_client()

    await client.connect()
    assert backend.connected is True

    await client.disconnect()
    assert backend.connected is False


@pytest.mark.asyncio
async def test_read_and_write_characteristics() -> None:
    client, backend = make_client()

    assert await client.read("read-char") == b"value"
    await client.write("write-char", b"command", response=False)

    assert backend.writes == [("write-char", b"command", False)]


@pytest.mark.asyncio
async def test_subscribe_forwards_notifications_and_unsubscribes() -> None:
    client, backend = make_client()
    values: list[bytes] = []

    await client.subscribe("notify-char", values.append)
    backend.callbacks["notify-char"](b"event")
    await client.unsubscribe("notify-char")

    assert values == [b"event"]
    assert backend.callbacks == {}


@pytest.mark.asyncio
async def test_async_context_manager_connects_and_disconnects() -> None:
    client, backend = make_client()

    async with client:
        assert backend.connected is True

    assert backend.connected is False


def test_pair_option_is_passed_to_backend() -> None:
    received_pair_options: list[bool] = []
    backend = FakeBleBackend("AA:BB:CC:DD:EE:FF")

    def backend_factory(address: str, pair: bool) -> FakeBleBackend:
        received_pair_options.append(pair)
        return backend

    BleClient(backend.address, pair=True, backend_factory=backend_factory)

    assert received_pair_options == [True]


def test_missing_bleak_raises_runtime_error() -> None:
    with patch(
        "klab_pytest_toolkit_embedded.ble.client.import_module",
        side_effect=ImportError("no bleak"),
    ):
        with pytest.raises(RuntimeError, match="ble"):
            BleClient("AA:BB:CC:DD:EE:FF")
