"""I2C controller interface definition for HIL setups."""

import abc


class I2cController(abc.ABC):
    """Abstract interface for I2C controllers used in HIL setups."""

    @abc.abstractmethod
    def write(self, address: int, data: bytes) -> None:
        """Write bytes to an I2C slave address."""
        raise NotImplementedError

    @abc.abstractmethod
    def read(self, address: int, count: int) -> bytes:
        """Read bytes from an I2C slave address."""
        raise NotImplementedError

    def write_read(self, address: int, tx_data: bytes, rx_count: int) -> bytes:
        """Write bytes, then read bytes from an I2C slave address."""
        self.write(address, tx_data)
        return self.read(address, rx_count)

    @abc.abstractmethod
    def close(self) -> None:
        """Close the I2C controller connection."""
        raise NotImplementedError

    def __enter__(self) -> "I2cController":
        """Enter context manager."""
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """Exit context manager and ensure cleanup."""
        self.close()
