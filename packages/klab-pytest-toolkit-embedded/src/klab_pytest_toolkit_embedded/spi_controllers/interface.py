"""SPI controller interface definition for HIL setups."""

import abc


class SpiController(abc.ABC):
    """Abstract interface for SPI controllers used in HIL setups."""

    @abc.abstractmethod
    def transfer(self, tx_data: bytes) -> bytes:
        """Transfer bytes over SPI and return received bytes."""
        raise NotImplementedError

    @abc.abstractmethod
    def close(self) -> None:
        """Close the SPI controller connection."""
        raise NotImplementedError

    def __enter__(self) -> "SpiController":
        """Enter context manager."""
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """Exit context manager and ensure cleanup."""
        self.close()
