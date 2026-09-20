"""Communication interface definition for embedded boards."""

import abc


class CommunicatorInterface(abc.ABC):
    """Abstract interface for device communication."""

    @abc.abstractmethod
    def send(self, data: bytes) -> None:
        """Send data to the device."""
        raise NotImplementedError

    @abc.abstractmethod
    def receive(self, num_bytes: int) -> bytes:
        """Receive data from the device."""
        raise NotImplementedError

    def read_line(self) -> bytes:
        """Read bytes up to and including the next newline.

        The default implementation reads one byte at a time via ``receive``.
        Concrete communicators may override this for efficiency.
        """
        data = bytearray()
        while True:
            chunk = self.receive(1)
            if not chunk:
                break
            data.extend(chunk)
            if chunk == b"\n":
                break
        return bytes(data)

    @abc.abstractmethod
    def close(self) -> None:
        """Close the communication channel."""
        raise NotImplementedError
