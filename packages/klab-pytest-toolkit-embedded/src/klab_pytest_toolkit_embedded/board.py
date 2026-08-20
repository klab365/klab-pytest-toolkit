import re
import time
from re import Pattern
from typing import cast

from klab_pytest_toolkit_embedded.communicators import CommunicatorInterface
from klab_pytest_toolkit_embedded.debug_probes import DebugProbe


class Board:
    """Main class for the orchestration of board operations.

    A board can be composed of optional capabilities such as a debug probe
    and a communication interface.
    """

    def __init__(
        self,
        debug_probe: DebugProbe | None = None,
        communicator: CommunicatorInterface | None = None,
    ):
        """Initialize the board.

        Args:
            debug_probe: Debug probe instance (e.g., EspTool)
            communicator: Communication interface instance (e.g., SerialCommunicator)
        """
        self._debug_probe = debug_probe
        self._communicator = communicator

    def _require_debug_probe(self) -> DebugProbe:
        if self._debug_probe is None:
            raise RuntimeError("This board has no debug probe")
        return self._debug_probe

    def _require_communicator(self) -> CommunicatorInterface:
        if self._communicator is None:
            raise RuntimeError("This board has no communicator")
        return self._communicator

    def program(self, fw_image: str) -> None:
        """Flash the firmware image to the board.

        Args:
            fw_image: Path to the firmware image.
        """
        self._require_debug_probe().program(fw_image)

    def reset(self) -> None:
        """Reset the board."""
        self._require_debug_probe().reset()

    def receive_some(self, num_bytes: int = 1024) -> bytes:
        """Receive some data from the communication interface.

        Args:
            num_bytes: Number of bytes to receive. Defaults to 1024.

        Returns:
            Received data.
        """
        return self._require_communicator().receive(num_bytes)

    def send(self, data: bytes) -> None:
        """Send data to the device through the communication interface.

        Args:
            data: Bytes to send
        """
        self._require_communicator().send(data)

    def wait_for_regex_in_line(
        self,
        regex: str | bytes | Pattern[str] | Pattern[bytes],
        timeout_s: float = 20,
        log: bool = True,
    ) -> bool:
        """Wait for a line matching the regex from the communication interface.

        Args:
            regex: Regular expression to match.
            timeout_s: Timeout in seconds. Defaults to 20.
            log: Whether to log the output. Defaults to True.

        Returns:
            True if a matching line is found.
        """
        buffer = b""
        start_time = time.monotonic()
        while True:
            if time.monotonic() - start_time > timeout_s:
                raise TimeoutError(f"Timeout waiting for regex: {regex!r}")

            chunk = self.receive_some()
            if log and chunk:
                print(chunk.replace(b"\r", b"").decode("utf-8", errors="ignore"), end="")
            buffer += chunk

            lines = buffer.splitlines(keepends=True)
            if buffer and buffer[-1:] not in (b"\n", b"\r"):
                complete_lines = lines[:-1]
                buffer = lines[-1]
            else:
                complete_lines = lines
                buffer = b""

            for line in complete_lines:
                normalized = line.replace(b"\r", b"").replace(b"\n", b"")
                if self._line_matches(regex, normalized):
                    return True

    @staticmethod
    def _line_matches(regex: str | bytes | Pattern[str] | Pattern[bytes], line: bytes) -> bool:
        if isinstance(regex, bytes):
            return re.search(regex, line) is not None

        if isinstance(regex, str):
            return re.search(regex, line.decode("utf-8", errors="ignore")) is not None

        if isinstance(regex.pattern, bytes):
            bytes_regex = cast(Pattern[bytes], regex)
            return bytes_regex.search(line) is not None

        str_regex = cast(Pattern[str], regex)
        return str_regex.search(line.decode("utf-8", errors="ignore")) is not None

    def __enter__(self):
        """Enter context manager."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit context manager."""
        errors = []
        for resource in (self._communicator, self._debug_probe):
            if resource is None:
                continue
            try:
                resource.close()
            except Exception as exc:
                errors.append(exc)
        if errors:
            raise errors[0]
