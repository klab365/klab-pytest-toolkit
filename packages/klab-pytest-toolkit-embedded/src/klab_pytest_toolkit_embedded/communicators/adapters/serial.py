"""Serial communication implementation for embedded boards."""

import serial

from klab_pytest_toolkit_embedded.communicators.interface import CommunicatorInterface


class SerialCommunicator(CommunicatorInterface):
    """Serial port communication interface for UART/USB connections."""

    def __init__(
        self,
        port: str,
        baudrate: int = 115200,
        timeout: float = 1.0,
        bytesize: int = serial.EIGHTBITS,
        parity: str = serial.PARITY_NONE,
        stopbits: float = serial.STOPBITS_ONE,
    ):
        """Initialize serial communication.

        Args:
            port: Serial port path (e.g., '/dev/ttyUSB0', 'COM3')
            baudrate: Communication speed in bits per second (default: 115200)
            timeout: Read timeout in seconds (default: 1.0)
            bytesize: Number of data bits (default: 8)
            parity: Parity checking mode (default: None)
            stopbits: Number of stop bits (default: 1)
        """
        self.port = port
        self.baudrate = baudrate
        self._serial: serial.Serial | None = None

        # Open the serial connection
        self._serial = serial.Serial(
            port=port,
            baudrate=baudrate,
            timeout=timeout,
            bytesize=bytesize,
            parity=parity,
            stopbits=stopbits,
        )

    def send(self, data: bytes) -> None:
        """Send data to the device.

        Args:
            data: Bytes to send

        Raises:
            RuntimeError: If serial port is not open
        """
        if not self._serial or not self._serial.is_open:
            raise RuntimeError("Serial port is not open")

        self._serial.write(data)
        self._serial.flush()

    def receive(self, num_bytes: int) -> bytes:
        """Receive data from the device.

        Args:
            num_bytes: Maximum number of bytes to receive

        Returns:
            Received bytes (may be less than num_bytes if timeout occurs)

        Raises:
            RuntimeError: If serial port is not open
        """
        if not self._serial or not self._serial.is_open:
            raise RuntimeError("Serial port is not open")

        return self._serial.read(num_bytes)

    def close(self) -> None:
        """Close the serial connection."""
        if self._serial and self._serial.is_open:
            self._serial.close()

    def flush_input(self) -> None:
        """Flush input buffer, discarding all pending data."""
        if self._serial and self._serial.is_open:
            self._serial.reset_input_buffer()

    def flush_output(self) -> None:
        """Flush output buffer, waiting for all data to be transmitted."""
        if self._serial and self._serial.is_open:
            self._serial.reset_output_buffer()

    def bytes_available(self) -> int:
        """Get number of bytes available in the input buffer.

        Returns:
            Number of bytes available to read
        """
        if not self._serial or not self._serial.is_open:
            return 0

        return self._serial.in_waiting

    def __enter__(self) -> "SerialCommunicator":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - ensures cleanup."""
        self.close()

    def __repr__(self) -> str:
        """String representation."""
        status = "open" if (self._serial and self._serial.is_open) else "closed"
        return f"<SerialCommunicator(port='{self.port}', baudrate={self.baudrate}, {status})>"
