"""Unit tests for the FtdiGpioController class."""

from typing import cast

import pytest

from klab_pytest_toolkit_embedded.gpio_controllers import FtdiGpioController


class MockFtdiBackend:
    def __init__(self, url: str, direction: int) -> None:
        self.url = url
        self.direction = direction
        self.state = 0
        self.closed = False

    def write_pin(self, bit: int, value: bool) -> None:
        if value:
            self.state |= 1 << bit
        else:
            self.state &= ~(1 << bit)

    def read_pin(self, bit: int) -> bool:
        return bool(self.state & (1 << bit))

    def close(self) -> None:
        self.closed = True


def test_ftdi_gpio_accepts_named_pins() -> None:
    gpio = FtdiGpioController(
        url="ftdi://ftdi:232h:1/1",
        pins={"reset_n": 0, "boot0": 1},
        backend_factory=MockFtdiBackend,
    )

    assert gpio.pin("reset_n") == 0
    assert gpio.pins == {"reset_n": 0, "boot0": 1}


def test_ftdi_gpio_read_write_and_close() -> None:
    gpio = FtdiGpioController(
        url="ftdi://ftdi:232h:1/1",
        pins={"reset_n": 0, "boot0": 1},
        backend_factory=MockFtdiBackend,
    )

    gpio.set_high("boot0")
    assert gpio.read("boot0") is True

    gpio.set_low("boot0")
    assert gpio.read("boot0") is False

    backend = cast(MockFtdiBackend, gpio._backend)
    gpio.close()
    assert backend.closed is True


def test_ftdi_gpio_allows_custom_direction_mask() -> None:
    gpio = FtdiGpioController(
        url="ftdi://ftdi:232h:1/1",
        pins={"reset_n": 0, "boot0": 2},
        direction=0b101,
        backend_factory=MockFtdiBackend,
    )

    backend = cast(MockFtdiBackend, gpio._backend)
    assert backend.direction == 0b101


def test_ftdi_gpio_requires_named_pins() -> None:
    with pytest.raises(ValueError, match="pins"):
        FtdiGpioController(
            url="ftdi://ftdi:232h:1/1",
            pins={},
            backend_factory=MockFtdiBackend,
        )
