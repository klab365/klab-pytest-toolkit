"""Communication interface definition for embedded boards."""

import abc


class CommunicatorInterface(abc.ABC):
    """Abstract interface for MCU communication."""

    @abc.abstractmethod
    def send(self, data: bytes) -> None:
        """Send data to the device."""
        raise NotImplementedError

    @abc.abstractmethod
    def receive(self, num_bytes: int) -> bytes:
        """Receive data from the device."""
        raise NotImplementedError

    @abc.abstractmethod
    def close(self) -> None:
        """Close the communication channel."""
        raise NotImplementedError
