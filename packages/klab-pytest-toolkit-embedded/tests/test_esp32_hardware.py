import pytest

from pathlib import Path
from typing import Generator
from klab_pytest_toolkit_embedded.board import Board
from klab_pytest_toolkit_embedded.debug_probes import EspTool
from klab_pytest_toolkit_embedded.communicators import SerialCommunicator

# Hardware-only tests.
#
# This file is excluded by default in pyproject.toml's [tool.pytest.ini_options]
# (`addopts = "--ignore=…/test_esp32_hardware.py"`) because it requires a
# physical ESP32 board connected at /dev/ttyUSB0.
#
# To run these tests locally on a machine that has the hardware:
#
#     uv run pytest packages/klab-pytest-toolkit-embedded/tests/test_esp32_hardware.py
#
# Or temporarily override the ignore:
#
#     uv run pytest --override-ini="addopts=" packages/klab-pytest-toolkit-embedded/tests/test_esp32_hardware.py


@pytest.fixture
def dut() -> Generator[Board]:
    PORT = "/dev/ttyUSB0"

    communicator = SerialCommunicator(port=PORT, baudrate=115200)
    debug_probe = EspTool(port=PORT, baudrate=1500000, address="0x0")
    with Board(debug_probe=debug_probe, communicator=communicator) as board:
        yield board


@pytest.mark.skipif(
    True,
    reason="This test programs the firmware to a physical ESP32 device. "
    "Remove this skipif when you have the hardware connected.",
)
def test_program_should_flash_firmware(dut: Board) -> None:
    test_dir = Path(__file__).parent
    firmware_file = test_dir / "assets" / "firmwares" / "m5stack-atom-demo.bin"

    # act
    dut.program(str(firmware_file))

    # assert
    # If no exception is raised, we assume the programming was successful.
    assert True


@pytest.mark.skipif(
    True,
    reason="This test programs the firmware to a physical ESP32 device. "
    "Remove this skipif when you have the hardware connected.",
)
def test_wait_until_boot_up_message_shown_up(dut: Board) -> None:
    test_dir = Path(__file__).parent
    firmware_file = test_dir / "assets" / "firmwares" / "m5stack-atom-demo.bin"
    dut.program(str(firmware_file))

    # act and assert
    boot_message = b"Firmware Ready!"
    assert dut.wait_for_regex_in_line(boot_message, timeout_s=10, log=True)
