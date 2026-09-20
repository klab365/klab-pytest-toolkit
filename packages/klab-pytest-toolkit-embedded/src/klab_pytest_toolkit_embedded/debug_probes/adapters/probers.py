"""probe-rs debug probe implementation for embedded boards."""

from __future__ import annotations

import subprocess
from collections.abc import Sequence

from klab_pytest_toolkit_embedded.debug_probes.interface import DebugProbe


class ProbeRsProbe(DebugProbe):
    """Debug probe implementation backed by the probe-rs CLI."""

    def __init__(
        self,
        chip: str,
        *,
        executable: str = "probe-rs",
        probe: str | None = None,
        protocol: str | None = None,
        speed_khz: int | None = None,
        connect_under_reset: bool = False,
        extra_args: Sequence[str] = (),
    ) -> None:
        self._chip = chip
        self._executable = executable
        self._probe = probe
        self._protocol = protocol
        self._speed_khz = speed_khz
        self._connect_under_reset = connect_under_reset
        self._extra_args = tuple(extra_args)

    def program(self, fw_image: str) -> None:
        """Flash the firmware image to the target device."""
        cmd = self._base_command("download", fw_image)
        subprocess.run(cmd, check=True)

    def reset(self) -> None:
        """Reset the target device."""
        cmd = self._base_command("reset")
        subprocess.run(cmd, check=True)

    def close(self) -> None:
        """Close the debug probe connection."""
        # probe-rs is invoked per operation, so there is no persistent connection.
        pass

    def _base_command(self, command: str, *command_args: str) -> list[str]:
        cmd = [self._executable, command, "--chip", self._chip]

        if self._probe is not None:
            cmd.extend(["--probe", self._probe])

        if self._protocol is not None:
            cmd.extend(["--protocol", self._protocol])

        if self._speed_khz is not None:
            cmd.extend(["--speed", str(self._speed_khz)])

        if self._connect_under_reset:
            cmd.append("--connect-under-reset")

        cmd.extend(self._extra_args)
        cmd.extend(command_args)
        return cmd

    def __repr__(self) -> str:
        return f"<ProbeRsProbe(chip={self._chip!r}, executable={self._executable!r})>"
