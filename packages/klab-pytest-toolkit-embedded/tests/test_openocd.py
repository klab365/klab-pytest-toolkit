"""Unit tests for the OpenOcdProbe class."""

from subprocess import CalledProcessError
from unittest.mock import patch

import pytest

from klab_pytest_toolkit_embedded.debug_probes import OpenOcdProbe


def test_program_uses_openocd_with_required_configs() -> None:
    probe = OpenOcdProbe(
        config_files=("interface/stlink.cfg", "target/stm32f4x.cfg"),
    )

    with patch("klab_pytest_toolkit_embedded.debug_probes.openocd.subprocess.run") as mock_run:
        probe.program("build/firmware.elf")

    mock_run.assert_called_once_with(
        [
            "openocd",
            "-f",
            "interface/stlink.cfg",
            "-f",
            "target/stm32f4x.cfg",
            "-c",
            "program build/firmware.elf verify reset exit",
        ],
        check=True,
    )


def test_program_supports_search_dirs_init_commands_extra_args_and_flash_address() -> None:
    probe = OpenOcdProbe(
        config_files=("interface/stlink.cfg", "target/stm32f4x.cfg"),
        executable="openocd-custom",
        search_dirs=("/opt/openocd/scripts",),
        init_commands=("adapter speed 4000",),
        extra_args=("-d2",),
        flash_address="0x08000000",
    )

    with patch("klab_pytest_toolkit_embedded.debug_probes.openocd.subprocess.run") as mock_run:
        probe.program("build/firmware.bin")

    mock_run.assert_called_once_with(
        [
            "openocd-custom",
            "-s",
            "/opt/openocd/scripts",
            "-f",
            "interface/stlink.cfg",
            "-f",
            "target/stm32f4x.cfg",
            "-c",
            "adapter speed 4000",
            "-c",
            "program build/firmware.bin 0x08000000 verify reset exit",
            "-d2",
        ],
        check=True,
    )


def test_reset_uses_openocd_reset_run() -> None:
    probe = OpenOcdProbe(
        config_files=("interface/stlink.cfg", "target/stm32f4x.cfg"),
    )

    with patch("klab_pytest_toolkit_embedded.debug_probes.openocd.subprocess.run") as mock_run:
        probe.reset()

    mock_run.assert_called_once_with(
        [
            "openocd",
            "-f",
            "interface/stlink.cfg",
            "-f",
            "target/stm32f4x.cfg",
            "-c",
            "init",
            "-c",
            "reset run",
            "-c",
            "shutdown",
        ],
        check=True,
    )


def test_openocd_errors_are_propagated() -> None:
    probe = OpenOcdProbe(
        config_files=("interface/stlink.cfg", "target/stm32f4x.cfg"),
    )

    with patch(
        "klab_pytest_toolkit_embedded.debug_probes.openocd.subprocess.run",
        side_effect=CalledProcessError(1, ["openocd"]),
    ):
        with pytest.raises(CalledProcessError):
            probe.program("build/firmware.elf")


def test_close_is_a_no_op() -> None:
    probe = OpenOcdProbe(
        config_files=("interface/stlink.cfg", "target/stm32f4x.cfg"),
    )

    probe.close()


def test_openocd_accepts_single_board_config() -> None:
    probe = OpenOcdProbe(config_files=("board/st_nucleo_f4.cfg",))

    with patch("klab_pytest_toolkit_embedded.debug_probes.openocd.subprocess.run") as mock_run:
        probe.reset()

    mock_run.assert_called_once_with(
        [
            "openocd",
            "-f",
            "board/st_nucleo_f4.cfg",
            "-c",
            "init",
            "-c",
            "reset run",
            "-c",
            "shutdown",
        ],
        check=True,
    )


def test_openocd_requires_at_least_one_config_file() -> None:
    with pytest.raises(ValueError, match="config_files"):
        OpenOcdProbe(config_files=())
