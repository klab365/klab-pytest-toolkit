"""Unit tests for the I2cController interface."""

from klab_pytest_toolkit_embedded.i2c_controllers import I2cController


class MockI2cController(I2cController):
    def __init__(self) -> None:
        self.storage = {}
        self.closed = False

    def write(self, address: int, data: bytes) -> None:
        self.storage[address] = data

    def read(self, address: int, count: int) -> bytes:
        return self.storage.get(address, b"")[:count]

    def close(self) -> None:
        self.closed = True


def test_i2c_controller_write_read() -> None:
    i2c = MockI2cController()
    i2c.write(0x42, b"\x01\x02\x03")
    assert i2c.read(0x42, 2) == b"\x01\x02"


def test_i2c_controller_write_read_helper() -> None:
    i2c = MockI2cController()
    i2c.write(0x50, b"\xaa\xbb")
    assert i2c.write_read(0x50, b"\x11\x22", 2) == b"\x11\x22"


def test_i2c_controller_context_manager_closes() -> None:
    i2c = MockI2cController()
    with i2c as active_i2c:
        assert active_i2c is i2c
    assert i2c.closed is True
