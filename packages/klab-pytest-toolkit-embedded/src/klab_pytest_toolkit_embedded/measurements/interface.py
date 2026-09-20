"""Measurement instrument interface for HIL setups."""

from typing import Protocol

from klab_pytest_toolkit_embedded.measurements.values import (
    Current,
    Resistance,
    Temperature,
    Voltage,
)


class MeasurementInstrument(Protocol):
    """Measure standard electrical quantities and temperature."""

    def measure_current(self) -> Current:
        """Return the measured electrical current."""
        ...

    def measure_voltage(self) -> Voltage:
        """Return the measured electrical voltage."""
        ...

    def measure_resistance(self) -> Resistance:
        """Return the measured electrical resistance."""
        ...

    def measure_temperature(self) -> Temperature:
        """Return the measured temperature."""
        ...
