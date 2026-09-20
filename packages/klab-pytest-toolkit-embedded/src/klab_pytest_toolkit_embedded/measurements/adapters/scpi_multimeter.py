"""SCPI digital multimeter adapter."""

from klab_pytest_toolkit_embedded.measurements.adapters.scpi import ScpiInstrument
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


class ScpiMultimeter(ScpiInstrument):
    """SCPI digital multimeter implementing the measurement instrument protocol.

    Measurements are returned in SI base units (volts, amperes, ohms, hertz, and
    degrees Celsius). Use the DTO ``to()`` method to convert to a preferred unit.
    """

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
