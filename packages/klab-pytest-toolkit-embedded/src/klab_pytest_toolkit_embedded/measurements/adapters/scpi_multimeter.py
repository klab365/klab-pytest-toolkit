"""SCPI digital multimeter adapter."""

import re

from klab_pytest_toolkit_embedded.communicators import CommunicatorInterface
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

_NUMBER = re.compile(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?")


class ScpiMultimeter:
    """SCPI digital multimeter implementing the measurement instrument protocol.

    Measurements are returned in SI base units (volts, amperes, ohms, hertz, and
    degrees Celsius). Use the DTO ``to()`` method to convert to a preferred unit.
    """

    def __init__(self, communicator: CommunicatorInterface) -> None:
        self._communicator = communicator

    def identify(self) -> str:
        """Return the instrument identification string (``*IDN?``)."""
        return self._query("*IDN?")

    def reset(self) -> None:
        """Reset the instrument to its default state (``*RST``)."""
        self._write("*RST")

    def measure_voltage(self) -> Voltage:
        """Measure DC voltage."""
        return self.measure_dc_voltage()

    def measure_dc_voltage(self) -> Voltage:
        """Measure DC voltage."""
        return Voltage(self._query_float("MEASure:VOLTage:DC?"), VoltageUnit.VOLT)

    def measure_ac_voltage(self) -> Voltage:
        """Measure AC voltage."""
        return Voltage(self._query_float("MEASure:VOLTage:AC?"), VoltageUnit.VOLT)

    def measure_current(self) -> Current:
        """Measure DC current."""
        return self.measure_dc_current()

    def measure_dc_current(self) -> Current:
        """Measure DC current."""
        return Current(self._query_float("MEASure:CURRent:DC?"), CurrentUnit.AMPERE)

    def measure_ac_current(self) -> Current:
        """Measure AC current."""
        return Current(self._query_float("MEASure:CURRent:AC?"), CurrentUnit.AMPERE)

    def measure_resistance(self) -> Resistance:
        """Measure two-wire resistance."""
        return Resistance(self._query_float("MEASure:RESistance?"), ResistanceUnit.OHM)

    def measure_resistance_4w(self) -> Resistance:
        """Measure four-wire resistance."""
        return Resistance(self._query_float("MEASure:FRESistance?"), ResistanceUnit.OHM)

    def measure_frequency(self) -> Frequency:
        """Measure frequency."""
        return Frequency(self._query_float("MEASure:FREQuency?"), FrequencyUnit.HERTZ)

    def measure_temperature(self) -> Temperature:
        """Measure temperature."""
        return Temperature(self._query_float("MEASure:TEMPerature?"), TemperatureUnit.CELSIUS)

    def close(self) -> None:
        """Close the underlying communicator."""
        self._communicator.close()

    def _write(self, command: str) -> None:
        self._communicator.send(f"{command}\n".encode())

    def _query(self, command: str) -> str:
        self._write(command)
        return self._communicator.read_line().decode().strip()

    def _query_float(self, command: str) -> float:
        raw = self._query(command)
        match = _NUMBER.search(raw)
        if match is None:
            raise ValueError(f"Unexpected SCPI response for {command!r}: {raw!r}")
        return float(match.group())

    def __enter__(self) -> "ScpiMultimeter":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()
