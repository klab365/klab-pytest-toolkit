"""Unit tests for the ProbeRsProbe class."""

from subprocess import CalledProcessError
from unittest.mock import patch

import pytest

from klab_pytest_toolkit_embedded.debug_probes import ProbeRsProbe


def test_program_uses_probe_rs_with_required_chip() -> None:
    probe = ProbeRsProbe(chip="STM32F411CEUx")

    with patch("klab_pytest_toolkit_embedded.debug_probes.probers.subprocess.run") as mock_run:
        probe.program("build/firmware.elf")

    mock_run.assert_called_once_with(
        ["probe-rs", "download", "--chip", "STM32F411CEUx", "build/firmware.elf"],
        check=True,
    )


def test_program_supports_optional_probe_parameters() -> None:
    probe = ProbeRsProbe(
        chip="STM32F411CEUx",
        executable="probe-rs-cli",
        probe="0483:374B:066EFF515153878367144143",
        protocol="swd",
        speed_khz=4000,
        connect_under_reset=True,
        extra_args=("--log", "debug"),
    )

    with patch("klab_pytest_toolkit_embedded.debug_probes.probers.subprocess.run") as mock_run:
        probe.program("build/firmware.bin")

    mock_run.assert_called_once_with(
        [
            "probe-rs-cli",
            "download",
            "--chip",
            "STM32F411CEUx",
            "--probe",
            "0483:374B:066EFF515153878367144143",
            "--protocol",
            "swd",
            "--speed",
            "4000",
            "--connect-under-reset",
            "--log",
            "debug",
            "build/firmware.bin",
        ],
        check=True,
    )


def test_reset_uses_probe_rs_reset() -> None:
    probe = ProbeRsProbe(chip="STM32F411CEUx")

    with patch("klab_pytest_toolkit_embedded.debug_probes.probers.subprocess.run") as mock_run:
        probe.reset()

    mock_run.assert_called_once_with(
        ["probe-rs", "reset", "--chip", "STM32F411CEUx"],
        check=True,
    )


def test_probe_rs_errors_are_propagated() -> None:
    probe = ProbeRsProbe(chip="STM32F411CEUx")

    with patch(
        "klab_pytest_toolkit_embedded.debug_probes.probers.subprocess.run",
        side_effect=CalledProcessError(1, ["probe-rs"]),
    ):
        with pytest.raises(CalledProcessError):
            probe.program("build/firmware.elf")


def test_close_is_a_no_op() -> None:
    probe = ProbeRsProbe(chip="STM32F411CEUx")
    probe.close()
