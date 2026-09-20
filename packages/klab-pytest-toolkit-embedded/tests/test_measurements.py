"""Tests for measurement data transfer objects and the instrument protocol."""

import pytest

from klab_pytest_toolkit_embedded.measurements import (
    Current,
    CurrentUnit,
    MeasurementInstrument,
    Resistance,
    ResistanceUnit,
    Temperature,
    TemperatureUnit,
    Voltage,
    VoltageUnit,
)


class FakeMultimeter:
    """A fake meter implementing the measurement instrument protocol."""

    def measure_current(self) -> Current:
        return Current(125, CurrentUnit.MILLIAMPERE)

    def measure_voltage(self) -> Voltage:
        return Voltage(3300, VoltageUnit.MILLIVOLT)

    def measure_resistance(self) -> Resistance:
        return Resistance(4.7, ResistanceUnit.KILOOHM)

    def measure_temperature(self) -> Temperature:
        return Temperature(25, TemperatureUnit.CELSIUS)


def read_all(meter: MeasurementInstrument) -> tuple[float, float, float, float]:
    """Read every supported quantity from a measurement instrument."""
    return (
        meter.measure_current().to(CurrentUnit.MILLIAMPERE).value,
        meter.measure_voltage().to(VoltageUnit.VOLT).value,
        meter.measure_resistance().to(ResistanceUnit.OHM).value,
        meter.measure_temperature().to(TemperatureUnit.CELSIUS).value,
    )


def test_measurement_instrument_returns_unit_aware_values() -> None:
    assert read_all(FakeMultimeter()) == pytest.approx((125, 3.3, 4700, 25))


def test_temperature_converts_between_all_supported_units() -> None:
    temperature = Temperature(32, TemperatureUnit.FAHRENHEIT)

    assert temperature.to(TemperatureUnit.CELSIUS).value == pytest.approx(0)
    assert temperature.to(TemperatureUnit.KELVIN).value == pytest.approx(273.15)
