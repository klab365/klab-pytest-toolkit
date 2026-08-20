"""Unit tests for the FtdiSpiController class."""

from typing import cast

from klab_pytest_toolkit_embedded.spi_controllers import FtdiSpiController


class MockFtdiSpiBackend:
    def __init__(self, url: str, chip_select: int, frequency_hz: float, mode: int) -> None:
        self.url = url
        self.chip_select = chip_select
        self.frequency_hz = frequency_hz
        self.mode = mode
        self.closed = False

    def transfer(self, tx_data: bytes) -> bytes:
        return bytes(b ^ 0xFF for b in tx_data)

    def close(self) -> None:
        self.closed = True


def test_ftdi_spi_transfer_and_close() -> None:
    spi = FtdiSpiController(
        url="ftdi://ftdi:232h:1/1",
        chip_select=1,
        frequency_hz=2_000_000,
        mode=3,
        backend_factory=MockFtdiSpiBackend,
    )

    assert spi.transfer(b"\x00\x55") == b"\xff\xaa"
    backend = cast(MockFtdiSpiBackend, spi._backend)
    spi.close()
    assert backend.closed is True
