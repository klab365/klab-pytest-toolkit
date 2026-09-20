"""Shared SCPI instrument helpers."""

import re

from klab_pytest_toolkit_embedded.communicators import CommunicatorInterface

_NUMBER = re.compile(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?")


class ScpiInstrument:
    """Base class for SCPI instruments providing common command helpers."""

    def __init__(self, communicator: CommunicatorInterface) -> None:
        self._communicator = communicator

    def identify(self) -> str:
        """Return the instrument identification string (``*IDN?``)."""
        return self._query("*IDN?")

    def reset(self) -> None:
        """Reset the instrument to its default state (``*RST``)."""
        self._write("*RST")

    def close(self) -> None:
        """Close the underlying communicator."""
        self._communicator.close()

    def _write(self, command: str) -> None:
        self._communicator.send(f"{command}\n".encode())

    def _query(self, command: str) -> str:
        self._write(command)
        return self._communicator.read_line().decode().strip()

    def _query_float(self, command: str) -> float:
        raw = self._query(command)
        match = _NUMBER.search(raw)
        if match is None:
            raise ValueError(f"Unexpected SCPI response for {command!r}: {raw!r}")
        return float(match.group())

    @staticmethod
    def _format_value(value: float) -> str:
        """Format a float for an SCPI command, stripping float noise."""
        return f"{value:.12g}"

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()
