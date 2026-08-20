"""Unit tests for the FtdiI2cController class."""

from typing import cast

from klab_pytest_toolkit_embedded.i2c_controllers import FtdiI2cController


class MockFtdiI2cBackend:
    def __init__(self, url: str, frequency_hz: float) -> None:
        self.url = url
        self.frequency_hz = frequency_hz
        self.storage = {}
        self.closed = False

    def write(self, address: int, data: bytes) -> None:
        self.storage[address] = data

    def read(self, address: int, count: int) -> bytes:
        return self.storage.get(address, b"")[:count]

    def close(self) -> None:
        self.closed = True


def test_ftdi_i2c_write_read_and_close() -> None:
    i2c = FtdiI2cController(
        url="ftdi://ftdi:232h:1/1",
        frequency_hz=400_000,
        backend_factory=MockFtdiI2cBackend,
    )

    i2c.write(0x42, b"\x10\x20\x30")
    assert i2c.read(0x42, 2) == b"\x10\x20"
    backend = cast(MockFtdiI2cBackend, i2c._backend)
    i2c.close()
    assert backend.closed is True
