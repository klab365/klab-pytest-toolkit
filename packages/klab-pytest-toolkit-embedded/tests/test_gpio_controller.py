"""Unit tests for the GpioController interface."""

from unittest.mock import patch

from klab_pytest_toolkit_embedded.gpio_controllers import GpioController


class MockGpioController(GpioController):
    def __init__(self) -> None:
        self.values = {"reset": False}
        self.closed = False

    def write(self, pin: str, value: bool) -> None:
        self.values[pin] = value

    def read(self, pin: str) -> bool:
        return self.values[pin]

    def close(self) -> None:
        self.closed = True


def test_gpio_controller_setters_and_read() -> None:
    gpio = MockGpioController()

    gpio.set_high("reset")
    assert gpio.read("reset") is True

    gpio.set_low("reset")
    assert gpio.read("reset") is False


@patch("time.sleep")
def test_gpio_controller_pulse(mock_sleep) -> None:
    gpio = MockGpioController()

    gpio.pulse("reset", 0.05)

    mock_sleep.assert_called_once_with(0.05)
    assert gpio.read("reset") is False


def test_gpio_controller_context_manager_closes() -> None:
    gpio = MockGpioController()

    with gpio as active_gpio:
        assert active_gpio is gpio

    assert gpio.closed is True
