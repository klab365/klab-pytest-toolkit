"""Debug probe interface definition for embedded boards."""

import abc


class DebugProbe(abc.ABC):
    """Abstract base class for debug probes."""

    @abc.abstractmethod
    def program(self, fw_image: str) -> None:
        """Flash the firmware image to the target device.

        Args:
            fw_image (str): Path to the firmware image.
        """
        raise NotImplementedError("program method must be implemented by subclasses")

    @abc.abstractmethod
    def reset(self) -> None:
        """Reset the target device."""
        raise NotImplementedError("reset method must be implemented by subclasses")

    @abc.abstractmethod
    def close(self) -> None:
        """Close the debug probe connection."""
        raise NotImplementedError("close method must be implemented by subclasses")
