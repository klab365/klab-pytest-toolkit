"""Unit-aware measurement instruments and values for HIL test fixtures."""

from klab_pytest_toolkit_embedded.measurements.adapters import ScpiMultimeter, ScpiPowerSupply
from klab_pytest_toolkit_embedded.measurements.interface import (
    MeasurementInstrument,
    PowerSupply,
)
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
    "PowerSupply",
    "Resistance",
    "ResistanceUnit",
    "ScpiMultimeter",
    "ScpiPowerSupply",
    "Temperature",
    "TemperatureUnit",
    "Voltage",
    "VoltageUnit",
]
