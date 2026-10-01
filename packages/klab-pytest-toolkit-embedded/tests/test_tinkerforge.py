"""Unit tests for Tinkerforge HIL adapters."""

import sys
from types import ModuleType
from typing import cast

import pytest

from klab_pytest_toolkit_embedded.gpio_controllers import (
    TinkerforgeIO16GpioController,
    TinkerforgePin,
)
from klab_pytest_toolkit_embedded.tinkerforge import TinkerforgeConnection


class MockConnection:
    def __init__(self) -> None:
        self.connected_to: tuple[str, int] | None = None
        self.disconnect_calls = 0

    def connect(self, host: str, port: int) -> None:
        self.connected_to = (host, port)

    def disconnect(self) -> None:
        self.disconnect_calls += 1


class MockIO16Backend:
    def __init__(self, connection: TinkerforgeConnection, uid: str) -> None:
        self.connection = connection
        self.uid = uid
        self.configured: dict[TinkerforgePin, bool] = {}
        self.values: dict[TinkerforgePin, bool] = {}
        self.closed = False

    def configure_pin(self, pin: TinkerforgePin, output: bool) -> None:
        self.configured[pin] = output

    def write_pin(self, pin: TinkerforgePin, value: bool) -> None:
        self.values[pin] = value

    def read_pin(self, pin: TinkerforgePin) -> bool:
        return self.values.get(pin, False)

    def close(self) -> None:
        self.closed = True


def test_tinkerforge_connection_connects_and_disconnects_once() -> None:
    backend = MockConnection()
    connection = TinkerforgeConnection("brickd.local", 4223, connection_factory=lambda: backend)

    assert backend.connected_to == ("brickd.local", 4223)
    assert connection.client is backend

    connection.close()
    connection.close()
    assert backend.disconnect_calls == 1


def test_io16_backend_uses_io16_v2_channel_api(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeBricklet:
        DIRECTION_IN = "i"
        DIRECTION_OUT = "o"

        def __init__(self, uid: str, client: object) -> None:
            self.uid = uid
            self.client = client
            self.configuration_calls: list[tuple[int, str, bool]] = []
            self.selected_value_calls: list[tuple[int, bool]] = []
            self.values = [False] * 16

        def set_configuration(self, channel: int, direction: str, value: bool) -> None:
            self.configuration_calls.append((channel, direction, value))

        def set_selected_value(self, channel: int, value: bool) -> None:
            self.selected_value_calls.append((channel, value))
            self.values[channel] = value

        def get_value(self) -> list[bool]:
            return self.values

    module = ModuleType("tinkerforge.bricklet_io16_v2")
    setattr(module, "BrickletIO16V2", FakeBricklet)
    monkeypatch.setitem(sys.modules, "tinkerforge.bricklet_io16_v2", module)
    connection = TinkerforgeConnection(connection_factory=MockConnection)
    gpio = TinkerforgeIO16GpioController(
        connection,
        "io16uid",
        {"reset": TinkerforgePin(0), "ready": TinkerforgePin(15)},
        input_pins=("ready",),
    )

    backend = cast(FakeBricklet, gpio._backend._bricklet)
    assert backend.configuration_calls == [(0, "o", False), (15, "i", False)]

    gpio.set_high("reset")
    assert backend.selected_value_calls == [(0, True)]
    assert gpio.read("reset") is True

    connection.close()


def test_io16_gpio_configures_named_input_and_output_pins() -> None:
    connection = TinkerforgeConnection(connection_factory=MockConnection)
    pins = {"reset": TinkerforgePin(0), "ready": TinkerforgePin(15)}
    gpio = TinkerforgeIO16GpioController(
        connection,
        "io16uid",
        pins,
        input_pins=("ready",),
        backend_factory=MockIO16Backend,
    )

    backend = cast(MockIO16Backend, gpio._backend)
    assert gpio.pins == pins
    assert backend.uid == "io16uid"
    assert backend.configured == {pins["reset"]: True, pins["ready"]: False}

    gpio.set_high("reset")
    assert gpio.read("reset") is True
    assert gpio.read("ready") is False

    with pytest.raises(ValueError, match="input pin"):
        gpio.set_high("ready")

    gpio.close()
    assert backend.closed is True
    connection.close()


@pytest.mark.parametrize("channel", [-1, 16])
def test_tinkerforge_pin_rejects_invalid_channel(channel: int) -> None:
    with pytest.raises(ValueError):
        TinkerforgePin(channel)


def test_io16_gpio_rejects_empty_and_unknown_input_pins() -> None:
    connection = TinkerforgeConnection(connection_factory=MockConnection)

    with pytest.raises(ValueError, match="pins"):
        TinkerforgeIO16GpioController(
            connection,
            "io16uid",
            {},
            backend_factory=MockIO16Backend,
        )
    with pytest.raises(ValueError, match="unknown"):
        TinkerforgeIO16GpioController(
            connection,
            "io16uid",
            {"reset": TinkerforgePin(0)},
            input_pins=("ready",),
            backend_factory=MockIO16Backend,
        )

    connection.close()
