"""Unit-aware measurement instruments and values for HIL test fixtures."""

from klab_pytest_toolkit_embedded.measurements.adapters import ScpiMultimeter
from klab_pytest_toolkit_embedded.measurements.interface import MeasurementInstrument
from klab_pytest_toolkit_embedded.measurements.values import (
    Current,
    CurrentUnit,
    Frequency,
    FrequencyUnit,
    Resistance,
    ResistanceUnit,
    Temperature,
    TemperatureUnit,
    Voltage,
    VoltageUnit,
)

__all__ = [
    "Current",
    "CurrentUnit",
    "Frequency",
    "FrequencyUnit",
    "MeasurementInstrument",
    "Resistance",
    "ResistanceUnit",
    "ScpiMultimeter",
    "Temperature",
    "TemperatureUnit",
    "Voltage",
    "VoltageUnit",
]
