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


class PowerSupply(Protocol):
    """A programmable power supply."""

    def set_voltage(self, value: Voltage) -> None:
        """Set the output voltage."""
        ...

    def set_current_limit(self, value: Current) -> None:
        """Set the output current limit."""
        ...

    def enable_output(self) -> None:
        """Enable the output."""
        ...

    def disable_output(self) -> None:
        """Disable the output."""
        ...

    def measure_voltage(self) -> Voltage:
        """Measure the actual output voltage."""
        ...

    def measure_current(self) -> Current:
        """Measure the actual output current."""
        ...
