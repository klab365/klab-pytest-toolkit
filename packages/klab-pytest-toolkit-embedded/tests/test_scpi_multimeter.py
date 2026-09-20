"""Tests for the SCPI multimeter adapter."""

import pytest

from klab_pytest_toolkit_embedded.communicators import CommunicatorInterface
from klab_pytest_toolkit_embedded.measurements import (
    CurrentUnit,
    FrequencyUnit,
    ResistanceUnit,
    ScpiMultimeter,
    TemperatureUnit,
    VoltageUnit,
)


class FakeCommunicator(CommunicatorInterface):
    """A scripted communicator for testing."""

    def __init__(self, responses: dict[str, str]) -> None:
        self._responses = responses
        self.sent: list[str] = []
        self.closed = False

    def send(self, data: bytes) -> None:
        self.sent.append(data.decode().strip())

    def receive(self, num_bytes: int) -> bytes:
        return b""

    def read_line(self) -> bytes:
        return self._responses[self.sent[-1]].encode()

    def close(self) -> None:
        self.closed = True


def make_multimeter() -> tuple[ScpiMultimeter, FakeCommunicator]:
    communicator = FakeCommunicator(
        {
            "*IDN?": "Keysight,34465A",
            "MEASure:VOLTage:DC?": "+3.30000000E+00",
            "MEASure:VOLTage:AC?": "+1.00000000E+00",
            "MEASure:CURRent:DC?": "+1.25000000E-03",
            "MEASure:CURRent:AC?": "+2.00000000E-03",
            "MEASure:RESistance?": "+4.70000000E+03",
            "MEASure:FRESistance?": "+1.00000000E+03",
            "MEASure:FREQuency?": "+1.00000000E+06",
            "MEASure:TEMPerature?": "+2.50000000E+01",
        }
    )
    return ScpiMultimeter(communicator), communicator


def test_measure_voltage_returns_base_unit() -> None:
    multimeter, _ = make_multimeter()

    measurement = multimeter.measure_voltage()

    assert measurement.unit is VoltageUnit.VOLT
    assert measurement.value == pytest.approx(3.3)


def test_measure_current_returns_base_unit() -> None:
    multimeter, _ = make_multimeter()

    measurement = multimeter.measure_current()

    assert measurement.unit is CurrentUnit.AMPERE
    assert measurement.to(CurrentUnit.MILLIAMPERE).value == pytest.approx(1.25)


def test_measure_resistance_returns_base_unit() -> None:
    multimeter, _ = make_multimeter()

    measurement = multimeter.measure_resistance()

    assert measurement.unit is ResistanceUnit.OHM
    assert measurement.to(ResistanceUnit.KILOOHM).value == pytest.approx(4.7)


def test_measure_temperature_returns_celsius() -> None:
    multimeter, _ = make_multimeter()

    measurement = multimeter.measure_temperature()

    assert measurement.unit is TemperatureUnit.CELSIUS
    assert measurement.value == pytest.approx(25)


def test_measure_ac_voltage() -> None:
    multimeter, _ = make_multimeter()

    measurement = multimeter.measure_ac_voltage()

    assert measurement.unit is VoltageUnit.VOLT
    assert measurement.value == pytest.approx(1.0)


def test_measure_ac_current() -> None:
    multimeter, _ = make_multimeter()

    measurement = multimeter.measure_ac_current()

    assert measurement.unit is CurrentUnit.AMPERE
    assert measurement.to(CurrentUnit.MILLIAMPERE).value == pytest.approx(2.0)


def test_measure_four_wire_resistance() -> None:
    multimeter, _ = make_multimeter()

    measurement = multimeter.measure_resistance_4w()

    assert measurement.unit is ResistanceUnit.OHM
    assert measurement.value == pytest.approx(1000)


def test_measure_frequency() -> None:
    multimeter, _ = make_multimeter()

    measurement = multimeter.measure_frequency()

    assert measurement.unit is FrequencyUnit.HERTZ
    assert measurement.to(FrequencyUnit.MEGAHERTZ).value == pytest.approx(1.0)


def test_identify_and_reset_use_standard_commands() -> None:
    multimeter, communicator = make_multimeter()

    assert multimeter.identify() == "Keysight,34465A"
    multimeter.reset()

    assert communicator.sent == ["*IDN?", "*RST"]


def test_close_delegates_to_communicator() -> None:
    multimeter, communicator = make_multimeter()

    multimeter.close()

    assert communicator.closed is True


def test_unexpected_response_raises_value_error() -> None:
    multimeter = ScpiMultimeter(FakeCommunicator({"MEASure:VOLTage:DC?": "OVERLOAD"}))

    with pytest.raises(ValueError, match="MEASure:VOLTage:DC"):
        multimeter.measure_voltage()
