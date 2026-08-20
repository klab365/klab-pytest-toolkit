"""Unit tests for the SpidevSpiController class."""

from typing import cast

from klab_pytest_toolkit_embedded.spi_controllers import SpidevSpiController


class MockSpidevBackend:
    def __init__(self, bus: int, device: int, max_speed_hz: int, mode: int) -> None:
        self.bus = bus
        self.device = device
        self.max_speed_hz = max_speed_hz
        self.mode = mode
        self.closed = False

    def transfer(self, tx_data: bytes) -> bytes:
        return bytes(reversed(tx_data))

    def close(self) -> None:
        self.closed = True


def test_spidev_spi_uses_bus_device_and_close() -> None:
    spi = SpidevSpiController(
        bus=0,
        device=1,
        max_speed_hz=2_000_000,
        mode=3,
        backend_factory=MockSpidevBackend,
    )

    assert spi.transfer(b"\x01\x02\x03") == b"\x03\x02\x01"

    backend = cast(MockSpidevBackend, spi._backend)
    assert backend.bus == 0
    assert backend.device == 1
    assert backend.max_speed_hz == 2_000_000
    assert backend.mode == 3

    spi.close()
    assert backend.closed is True
