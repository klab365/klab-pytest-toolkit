"""OpenOCD debug probe implementation for embedded boards."""

from __future__ import annotations

import subprocess
from collections.abc import Sequence

from klab_pytest_toolkit_embedded.debug_probes.interface import DebugProbe


class OpenOcdProbe(DebugProbe):
    """Debug probe implementation backed by the OpenOCD CLI."""

    def __init__(
        self,
        config_files: Sequence[str],
        *,
        executable: str = "openocd",
        search_dirs: Sequence[str] = (),
        init_commands: Sequence[str] = (),
        extra_args: Sequence[str] = (),
        flash_address: str | None = None,
    ) -> None:
        if not config_files:
            raise ValueError("config_files must contain at least one OpenOCD config")

        self._executable = executable
        self._config_files = tuple(config_files)
        self._search_dirs = tuple(search_dirs)
        self._init_commands = tuple(init_commands)
        self._extra_args = tuple(extra_args)
        self._flash_address = flash_address

    def program(self, fw_image: str) -> None:
        """Flash the firmware image to the target device."""
        flash_command = f"program {fw_image}"
        if self._flash_address is not None:
            flash_command += f" {self._flash_address}"
        flash_command += " verify reset exit"
        self._run_openocd(flash_command)

    def reset(self) -> None:
        """Reset the target device."""
        self._run_openocd("init", "reset run", "shutdown")

    def close(self) -> None:
        """Close the debug probe connection."""
        # OpenOCD is invoked per operation, so there is no persistent connection.
        pass

    def _run_openocd(self, *commands: str) -> None:
        cmd = [self._executable]

        for search_dir in self._search_dirs:
            cmd.extend(["-s", search_dir])

        for config_file in self._config_files:
            cmd.extend(["-f", config_file])

        for init_command in self._init_commands:
            cmd.extend(["-c", init_command])

        for command in commands:
            cmd.extend(["-c", command])

        cmd.extend(self._extra_args)

        subprocess.run(cmd, check=True)

    def __repr__(self) -> str:
        return (
            f"<OpenOcdProbe(config_files={self._config_files!r}, executable={self._executable!r})>"
        )
