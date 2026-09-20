"""Unit-aware measurement data transfer objects."""

from dataclasses import dataclass
from enum import StrEnum
from typing import Mapping


class CurrentUnit(StrEnum):
    """Supported electrical current units."""

    AMPERE = "A"
    MILLIAMPERE = "mA"
    MICROAMPERE = "uA"


class VoltageUnit(StrEnum):
    """Supported electrical voltage units."""

    VOLT = "V"
    MILLIVOLT = "mV"


class ResistanceUnit(StrEnum):
    """Supported electrical resistance units."""

    OHM = "ohm"
    KILOOHM = "kohm"
    MEGAOHM = "Mohm"


class TemperatureUnit(StrEnum):
    """Supported temperature units."""

    CELSIUS = "degC"
    FAHRENHEIT = "degF"
    KELVIN = "K"


def _convert_linear(
    value: float, from_unit: StrEnum, to_unit: StrEnum, factors: Mapping[StrEnum, float]
) -> float:
    """Convert a linear value via its SI base unit."""
    return value * factors[from_unit] / factors[to_unit]


@dataclass(frozen=True, slots=True)
class Current:
    """An electrical current measurement."""

    value: float
    unit: CurrentUnit

    def to(self, unit: CurrentUnit) -> "Current":
        """Convert this measurement to ``unit``."""
        factors: Mapping[StrEnum, float] = {
            CurrentUnit.AMPERE: 1.0,
            CurrentUnit.MILLIAMPERE: 1e-3,
            CurrentUnit.MICROAMPERE: 1e-6,
        }
        return Current(_convert_linear(self.value, self.unit, unit, factors), unit)


@dataclass(frozen=True, slots=True)
class Voltage:
    """An electrical voltage measurement."""

    value: float
    unit: VoltageUnit

    def to(self, unit: VoltageUnit) -> "Voltage":
        """Convert this measurement to ``unit``."""
        factors: Mapping[StrEnum, float] = {
            VoltageUnit.VOLT: 1.0,
            VoltageUnit.MILLIVOLT: 1e-3,
        }
        return Voltage(_convert_linear(self.value, self.unit, unit, factors), unit)


@dataclass(frozen=True, slots=True)
class Resistance:
    """An electrical resistance measurement."""

    value: float
    unit: ResistanceUnit

    def to(self, unit: ResistanceUnit) -> "Resistance":
        """Convert this measurement to ``unit``."""
        factors: Mapping[StrEnum, float] = {
            ResistanceUnit.OHM: 1.0,
            ResistanceUnit.KILOOHM: 1e3,
            ResistanceUnit.MEGAOHM: 1e6,
        }
        return Resistance(_convert_linear(self.value, self.unit, unit, factors), unit)


@dataclass(frozen=True, slots=True)
class Temperature:
    """A temperature measurement."""

    value: float
    unit: TemperatureUnit

    def to(self, unit: TemperatureUnit) -> "Temperature":
        """Convert this measurement to ``unit``."""
        celsius = self._to_celsius()
        return Temperature(self._from_celsius(celsius, unit), unit)

    def _to_celsius(self) -> float:
        """Convert this value to degrees Celsius."""
        match self.unit:
            case TemperatureUnit.CELSIUS:
                return self.value
            case TemperatureUnit.FAHRENHEIT:
                return (self.value - 32.0) * 5.0 / 9.0
            case TemperatureUnit.KELVIN:
                return self.value - 273.15

    @staticmethod
    def _from_celsius(value: float, unit: TemperatureUnit) -> float:
        """Convert degrees Celsius to ``unit``."""
        match unit:
            case TemperatureUnit.CELSIUS:
                return value
            case TemperatureUnit.FAHRENHEIT:
                return value * 9.0 / 5.0 + 32.0
            case TemperatureUnit.KELVIN:
                return value + 273.15
