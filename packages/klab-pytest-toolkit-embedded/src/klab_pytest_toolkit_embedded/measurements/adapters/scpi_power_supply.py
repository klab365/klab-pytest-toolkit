"""SCPI programmable power supply adapter."""

from klab_pytest_toolkit_embedded.measurements.adapters.scpi import ScpiInstrument
from klab_pytest_toolkit_embedded.measurements.values import (
    Current,
    CurrentUnit,
    Voltage,
    VoltageUnit,
)


class ScpiPowerSupply(ScpiInstrument):
    """SCPI programmable power supply.

    Values are written in SI base units (volts and amperes). On exit, the output is
    disabled before the communicator is closed, even when a test fails.
    """

    def set_voltage(self, value: Voltage) -> None:
        """Set the output voltage."""
        self._write(f"VOLTage {self._format_value(value.to(VoltageUnit.VOLT).value)}")

    def set_current_limit(self, value: Current) -> None:
        """Set the output current limit."""
        self._write(f"CURRent {self._format_value(value.to(CurrentUnit.AMPERE).value)}")

    def enable_output(self) -> None:
        """Enable the output."""
        self._write("OUTPut ON")

    def disable_output(self) -> None:
        """Disable the output."""
        self._write("OUTPut OFF")

    def measure_voltage(self) -> Voltage:
        """Measure the actual output voltage."""
        return Voltage(self._query_float("MEASure:VOLTage?"), VoltageUnit.VOLT)

    def measure_current(self) -> Current:
        """Measure the actual output current."""
        return Current(self._query_float("MEASure:CURRent?"), CurrentUnit.AMPERE)

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        try:
            self.disable_output()
        finally:
            self.close()
