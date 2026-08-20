"""Logic analyzer interface definition for HIL setups."""

import abc

from klab_pytest_toolkit_embedded.logic_analyzers.capture import LogicCapture


class LogicAnalyzer(abc.ABC):
    """Abstract interface for logic analyzers used in HIL setups."""

    @abc.abstractmethod
    def start_capture(self) -> None:
        """Start a capture session."""
        raise NotImplementedError

    @abc.abstractmethod
    def stop_capture(self) -> None:
        """Stop the current capture session."""
        raise NotImplementedError

    @abc.abstractmethod
    def export(self, path: str) -> None:
        """Export the captured data to a file."""
        raise NotImplementedError

    @abc.abstractmethod
    def get_capture(self) -> LogicCapture:
        """Return an object representing the current capture."""
        raise NotImplementedError

    @abc.abstractmethod
    def close(self) -> None:
        """Close the logic analyzer connection."""
        raise NotImplementedError

    def __enter__(self) -> "LogicAnalyzer":
        """Enter context manager."""
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """Exit context manager and ensure cleanup."""
        self.close()
