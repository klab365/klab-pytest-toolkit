"""GPIO controller interface definition for HIL setups."""

import abc
import time


class GpioController(abc.ABC):
    """Abstract interface for GPIO controllers used in HIL setups."""

    @abc.abstractmethod
    def write(self, pin: str, value: bool) -> None:
        """Write a boolean value to a named pin."""
        raise NotImplementedError

    def set_high(self, pin: str) -> None:
        """Set a named pin high."""
        self.write(pin, True)

    def set_low(self, pin: str) -> None:
        """Set a named pin low."""
        self.write(pin, False)

    @abc.abstractmethod
    def read(self, pin: str) -> bool:
        """Read a boolean value from a named pin."""
        raise NotImplementedError

    def pulse(self, pin: str, duration_s: float) -> None:
        """Drive a pin high for ``duration_s`` seconds, then low."""
        self.set_high(pin)
        time.sleep(duration_s)
        self.set_low(pin)

    @abc.abstractmethod
    def close(self) -> None:
        """Close the GPIO controller connection."""
        raise NotImplementedError

    def __enter__(self) -> "GpioController":
        """Enter context manager."""
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """Exit context manager and ensure cleanup."""
        self.close()
