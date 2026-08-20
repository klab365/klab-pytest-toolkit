"""Logic capture abstractions for HIL setups."""

import abc
from collections.abc import Mapping, Sequence


class LogicCapture(abc.ABC):
    """Abstract representation of a captured logic analyzer session."""

    @property
    @abc.abstractmethod
    def digital_channels(self) -> Mapping[str, int]:
        """Return the named digital channel mapping for this capture."""
        raise NotImplementedError

    @abc.abstractmethod
    def channel(self, name: str) -> int:
        """Resolve a named channel to its digital channel index."""
        raise NotImplementedError

    def has_channel(self, name: str) -> bool:
        """Return whether the capture contains the named channel."""
        return name in self.digital_channels

    def assert_has_channel(self, name: str) -> None:
        """Assert that the capture contains the named channel."""
        if not self.has_channel(name):
            raise AssertionError(f"Channel {name!r} not found in capture")

    def assert_has_channels(self, *names: str) -> None:
        """Assert that the capture contains all named channels."""
        missing = [name for name in names if not self.has_channel(name)]
        if missing:
            raise AssertionError(
                f"Channels not found in capture: {', '.join(repr(name) for name in missing)}"
            )

    @abc.abstractmethod
    def transitions(self, name: str) -> Sequence[float]:
        """Return transition timestamps for a named channel."""
        raise NotImplementedError

    def assert_any_activity(self, name: str) -> None:
        """Assert that the named channel has at least one transition."""
        self.assert_has_channel(name)
        if not self.transitions(name):
            raise AssertionError(f"Expected activity on channel {name!r}, but none was captured")

    def assert_no_activity(self, name: str) -> None:
        """Assert that the named channel has no transitions."""
        self.assert_has_channel(name)
        if self.transitions(name):
            raise AssertionError(
                f"Expected no activity on channel {name!r}, but transitions were captured"
            )

    def assert_toggles_at_least(self, name: str, count: int) -> None:
        """Assert that the named channel toggles at least ``count`` times."""
        self.assert_has_channel(name)
        actual_count = len(self.transitions(name))
        if actual_count < count:
            raise AssertionError(
                f"Expected channel {name!r} to toggle at least {count} times, got {actual_count}"
            )

    @abc.abstractmethod
    def export(self, path: str) -> None:
        """Export the capture to a file."""
        raise NotImplementedError
