import re
import time

from klab_pytest_toolkit_embedded.communicators import CommunicatorInterface
from klab_pytest_toolkit_embedded.debug_probes import DebugProbe


class Board:
    """Main class for the orchestration of board operations.

    This class uses a debug probe to program and reset the board,
    and a communication interface to send and receive data.

    It could be, that both functionalities are provided by the same physical device,
    but this is abstracted away by using separate interfaces.
    """

    def __init__(
        self,
        debug_probe: DebugProbe,
        communicator: CommunicatorInterface,
    ):
        """Initialize the board.

        Args:
            debug_probe: Debug probe instance (e.g., EspTool)
            communication_interface: Communication interface instance (e.g., SerialCommunicator)
        """
        self._debug_probe = debug_probe
        self._communicator = communicator

    def program(self, fw_image: str) -> None:
        """Flash the firmware image to the board.

        Args:
            fw_image (str): Path to the firmware image.
        """
        self._debug_probe.program(fw_image)

    def reset(self) -> None:
        """Reset the board."""
        self._debug_probe.reset()

    def receive_some(self, num_bytes: int = 1024) -> bytes:
        """Receive some data from the communication interface.

        Args:
            num_bytes (int, optional): Number of bytes to receive. Defaults to 1024.

        Returns:
            bytes: Received data.
        """
        return self._communicator.receive(num_bytes)

    def send(self, data: bytes) -> None:
        """Send data to the device through the communication interface.

        Args:
            data: Bytes to send
        """
        self._communicator.send(data)

    def wait_for_regex_in_line(self, regex, timeout_s=20, log=True) -> bool:
        """Wait for a line matching the regex from the communication interface.

        Args:
            regex: Regular expression to match.
            timeout_s (int, optional): Timeout in seconds. Defaults to 20.
            log (bool, optional): Whether to log the output. Defaults to True.

        Returns:
            bool: True if a matching line is found, False otherwise.
        """
        received = b""  # Start with bytes, not string
        start_time = time.time()
        while True:
            # Check for timeout
            if time.time() - start_time > timeout_s:
                raise TimeoutError(f"Timeout waiting for regex: {regex}")

            # Check in already received data
            lines = received.splitlines(keepends=True)

            for _, line in enumerate(lines):
                regex_search = re.search(
                    regex,
                    line.replace(b"\r", b"").replace(b"\n", b"").decode("utf-8", errors="ignore"),
                )
                if regex_search:
                    return True

            # Receive more data
            chunk = self.receive_some()

            if log:
                print(chunk.replace(b"\r", b"").decode("utf-8", errors="ignore"), end="")

            received = received + chunk

    def __enter__(self):
        """Enter context manager."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit context manager."""
        self._communicator.close()
        self._debug_probe.close()
