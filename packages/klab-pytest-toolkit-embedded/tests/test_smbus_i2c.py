"""Unit tests for the SmbusI2cController class."""

from typing import cast

from klab_pytest_toolkit_embedded.i2c_controllers import SmbusI2cController


class MockSmbusBackend:
    def __init__(self, bus: int) -> None:
        self.bus = bus
        self.storage = {}
        self.closed = False

    def write(self, address: int, data: bytes) -> None:
        self.storage[address] = data

    def read(self, address: int, count: int) -> bytes:
        return self.storage.get(address, b"")[:count]

    def close(self) -> None:
        self.closed = True


def test_smbus_i2c_uses_bus_number_and_close() -> None:
    i2c = SmbusI2cController(bus=3, backend_factory=MockSmbusBackend)

    i2c.write(0x42, b"\x10\x20\x30")
    assert i2c.read(0x42, 2) == b"\x10\x20"

    backend = cast(MockSmbusBackend, i2c._backend)
    assert backend.bus == 3

    i2c.close()
    assert backend.closed is True
