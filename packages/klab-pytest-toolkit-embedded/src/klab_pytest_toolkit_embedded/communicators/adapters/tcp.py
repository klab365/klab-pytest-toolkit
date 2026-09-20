"""TCP socket communication implementation for network-connected devices."""

import socket

from klab_pytest_toolkit_embedded.communicators.interface import CommunicatorInterface


class TcpCommunicator(CommunicatorInterface):
    """TCP socket communication interface (e.g., LXI instruments)."""

    def __init__(self, host: str, port: int, timeout: float = 5.0) -> None:
        self._host = host
        self._port = port
        self._socket = socket.create_connection((host, port), timeout=timeout)

    def send(self, data: bytes) -> None:
        """Send data to the device."""
        self._socket.sendall(data)

    def receive(self, num_bytes: int) -> bytes:
        """Receive data from the device."""
        return self._socket.recv(num_bytes)

    def close(self) -> None:
        """Close the TCP connection."""
        self._socket.close()

    def __enter__(self) -> "TcpCommunicator":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()
