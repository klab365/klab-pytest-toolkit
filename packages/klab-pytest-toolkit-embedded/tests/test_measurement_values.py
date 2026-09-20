"""Unit tests for measurement value DTOs."""

from dataclasses import FrozenInstanceError

import pytest

from klab_pytest_toolkit_embedded.measurements import (
    Current,
    CurrentUnit,
    Resistance,
    ResistanceUnit,
    Temperature,
    TemperatureUnit,
    Voltage,
    VoltageUnit,
)


@pytest.mark.parametrize(
    ("measurement", "target_unit", "expected_value"),
    [
        (Current(1.25, CurrentUnit.AMPERE), CurrentUnit.MILLIAMPERE, 1250),
        (Current(250, CurrentUnit.MICROAMPERE), CurrentUnit.AMPERE, 0.00025),
        (Voltage(3.3, VoltageUnit.VOLT), VoltageUnit.MILLIVOLT, 3300),
        (Voltage(500, VoltageUnit.MILLIVOLT), VoltageUnit.VOLT, 0.5),
        (Resistance(2.2, ResistanceUnit.KILOOHM), ResistanceUnit.OHM, 2200),
        (Resistance(1_000_000, ResistanceUnit.OHM), ResistanceUnit.MEGAOHM, 1),
    ],
)
def test_linear_measurements_convert_units(measurement, target_unit, expected_value) -> None:
    converted = measurement.to(target_unit)

    assert converted.unit is target_unit
    assert converted.value == pytest.approx(expected_value)


@pytest.mark.parametrize(
    ("measurement", "target_unit", "expected_value"),
    [
        (Temperature(0, TemperatureUnit.CELSIUS), TemperatureUnit.FAHRENHEIT, 32),
        (Temperature(100, TemperatureUnit.CELSIUS), TemperatureUnit.KELVIN, 373.15),
        (Temperature(32, TemperatureUnit.FAHRENHEIT), TemperatureUnit.CELSIUS, 0),
        (Temperature(273.15, TemperatureUnit.KELVIN), TemperatureUnit.CELSIUS, 0),
    ],
)
def test_temperature_converts_units(measurement, target_unit, expected_value) -> None:
    converted = measurement.to(target_unit)

    assert converted.unit is target_unit
    assert converted.value == pytest.approx(expected_value)


def test_measurement_values_are_immutable() -> None:
    current = Current(10, CurrentUnit.MILLIAMPERE)

    with pytest.raises(FrozenInstanceError):
        setattr(current, "value", 20)
