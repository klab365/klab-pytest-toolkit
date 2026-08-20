"""Unit tests for the SpiController interface."""

from klab_pytest_toolkit_embedded.spi_controllers import SpiController


class MockSpiController(SpiController):
    def __init__(self) -> None:
        self.closed = False

    def transfer(self, tx_data: bytes) -> bytes:
        return tx_data[::-1]

    def close(self) -> None:
        self.closed = True


def test_spi_controller_transfer() -> None:
    spi = MockSpiController()
    assert spi.transfer(b"\x01\x02\x03") == b"\x03\x02\x01"


def test_spi_controller_context_manager_closes() -> None:
    spi = MockSpiController()
    with spi as active_spi:
        assert active_spi is spi
    assert spi.closed is True
