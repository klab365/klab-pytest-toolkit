# Klab Pytest Toolkit - Embedded

[![PyPI](https://img.shields.io/pypi/v/klab-pytest-toolkit-embedded)](https://pypi.org/project/klab-pytest-toolkit-embedded/)
[![Python](https://img.shields.io/pypi/pyversions/klab-pytest-toolkit-embedded)](https://pypi.org/project/klab-pytest-toolkit-embedded/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../LICENSE)

Reusable embedded HIL testing components for pytest.
The goal is to allow testers to easily test embedded devices with reusable components for programming, resetting, communication, and test-bench control.

At the moment the package provides the following components:

- `Board`: Main orchestration class for managing board operations, including programming, resetting, and communication.
- Debug Probes:
  - `EspTool`: Debug probe implementation for ESP32 devices using `esptool`.
  - `OpenOcdProbe`: Generic debug probe implementation using the `openocd` CLI.
  - `ProbeRsProbe`: Generic debug probe implementation using the `probe-rs` CLI.
- Communicators:
  - `SerialCommunicator`: Serial port communication interface for UART/USB connections.
- Logic Analyzers:
  - `LogicAnalyzer`: Abstract interface for reusable logic analyzer fixtures.
  - `SaleaeLogicAnalyzer`: Saleae Automation API based implementation with named digital channels.
- GPIO Controllers:
  - `GpioController`: Abstract interface for reusable GPIO fixtures.
  - `FtdiGpioController`: FTDI/pyftdi based GPIO controller with named pins.
- SPI Controllers:
  - `SpiController`: Abstract interface for reusable SPI fixtures.
  - `FtdiSpiController`: FTDI/pyftdi based SPI controller.
  - `SpidevSpiController`: Linux spidev based SPI controller for Raspberry Pi and other Linux benches.
- I2C Controllers:
  - `I2cController`: Abstract interface for reusable I2C fixtures.
  - `FtdiI2cController`: FTDI/pyftdi based I2C controller.
  - `SmbusI2cController`: Linux SMBus/I2C controller for Raspberry Pi and other Linux benches.

## Installation

```bash
pip install klab-pytest-toolkit-embedded
```

Install Saleae support with the optional extra (pulls in `logic2-automation`):

```bash
pip install 'klab-pytest-toolkit-embedded[saleae]'
```

Install FTDI bench support with the optional extra:

```bash
pip install 'klab-pytest-toolkit-embedded[ftdi]'
```

Install Linux bench bus support with the optional extra:

```bash
pip install 'klab-pytest-toolkit-embedded[linux]'
```

At the moment, the `linux` extra is used for Linux SPI and I2C backends (`spidev` and `smbus2`). A Linux GPIO backend is planned separately.

## Usage

### Board Class

The `Board` class orchestrates board operations by combining optional capabilities such as a debug probe (for programming and resetting) and a communicator (for sending and receiving data).

**Create a fixture**

```python
import pytest
from pathlib import Path
from typing import Generator
from klab_pytest_toolkit_embedded.board import Board
from klab_pytest_toolkit_embedded.debug_probes import EspTool
from klab_pytest_toolkit_embedded.communicators import SerialCommunicator

@pytest.fixture
def dut() -> Generator[Board]:
    """Fixture to provide a Board instance for Device Under Test (DUT)."""
    PORT = "/dev/ttyUSB0"
    
    communicator = SerialCommunicator(port=PORT, baudrate=115200)
    debug_probe = EspTool(port=PORT, baudrate=1500000, address="0x0")
    
    with Board(debug_probe=debug_probe, communicator=communicator) as board:
        yield board
```

You can also create boards with only the dependencies they need:

```python
board_with_uart_only = Board(communicator=SerialCommunicator(port="/dev/ttyUSB0"))
board_with_probe_only = Board(debug_probe=EspTool(port="/dev/ttyUSB0"))
```

**Programming and Reset**

```python
def test_program_firmware(dut: Board):
    """Test programming firmware to the board."""
    firmware_file = "path/to/firmware.bin"
    dut.program(firmware_file)
    # Firmware is now flashed to the device

def test_reset_board(dut: Board):
    """Test resetting the board."""
    dut.reset()
    # Board has been reset
```

**Communication**

The `Board` class provides methods for sending and receiving data:

```python
def test_send_data(dut: Board):
    """Test sending data to the board."""
    dut.send(b"Hello Device!\n")

def test_receive_data(dut: Board):
    """Test receiving data from the board."""
    data = dut.receive_some(num_bytes=1024)
    print(data.decode('utf-8', errors='ignore'))

def test_wait_for_boot_message(dut: Board):
    """Test waiting for a specific message during boot."""
    firmware_file = "path/to/firmware.bin"
    dut.program(firmware_file)
    
    # Wait for boot message with regex
    boot_message = b"Firmware Ready!"
    assert dut.wait_for_regex_in_line(boot_message, timeout_s=10, log=True)
```

`wait_for_regex_in_line()` accepts `str`, `bytes`, and compiled regex patterns.

### Serial Communicator

The `SerialCommunicator` provides serial communication functionality with configurable parameters:

```python
from klab_pytest_toolkit_embedded.communicators import SerialCommunicator

# Create a serial communicator
communicator = SerialCommunicator(
    port="/dev/ttyUSB0",
    baudrate=115200,
    timeout=1.0
)

# Send data
communicator.send(b"AT\r\n")

# Receive data
data = communicator.receive(num_bytes=100)

# Check available bytes
available = communicator.bytes_available()

# Flush buffers
communicator.flush_input()
communicator.flush_output()

# Close when done
communicator.close()
```

### OpenOCD Debug Probe

The `OpenOcdProbe` class provides generic programming and reset functionality for boards supported by OpenOCD, including ST-Link based setups. Pass one or more OpenOCD config files, for example separate interface/target configs or a single board config:

```python
from klab_pytest_toolkit_embedded.debug_probes import OpenOcdProbe

probe = OpenOcdProbe(
    config_files=("interface/stlink.cfg", "target/stm32f4x.cfg"),
    search_dirs=("/usr/share/openocd/scripts",),
)

probe.program("build/firmware.elf")
probe.reset()

board_probe = OpenOcdProbe(
    config_files=("board/st_nucleo_f4.cfg",),
)
```

You can combine it with a serial communicator in a board fixture:

```python
@pytest.fixture
def dut() -> Generator[Board]:
    with Board(
        debug_probe=OpenOcdProbe(
            config_files=("interface/stlink.cfg", "target/stm32f4x.cfg"),
            search_dirs=("/usr/share/openocd/scripts",),
        ),
        communicator=SerialCommunicator(port="/dev/ttyACM0", baudrate=115200),
    ) as board:
        yield board
```

### probe-rs Debug Probe

The `ProbeRsProbe` class provides programming and reset functionality using the `probe-rs` CLI:

```python
from klab_pytest_toolkit_embedded.debug_probes import ProbeRsProbe

probe = ProbeRsProbe(
    chip="STM32F411CEUx",
    protocol="swd",
    speed_khz=4000,
)

probe.program("build/firmware.elf")
probe.reset()
```

You can also select a specific probe:

```python
probe = ProbeRsProbe(
    chip="STM32F411CEUx",
    probe="0483:374B:066EFF515153878367144143",
)
```

### ESP Debug Probe

The `EspTool` class provides programming and reset functionality for ESP32 devices:

```python
from klab_pytest_toolkit_embedded.debug_probes import EspTool

# Create ESP debug probe
esp_probe = EspTool(
    port="/dev/ttyUSB0",
    baudrate=1500000,
    address="0x0"
)

# Program firmware
esp_probe.program("path/to/firmware.bin")

# Reset the device
esp_probe.reset()

# Close (no persistent connection for esptool)
esp_probe.close()
```

### GPIO Controller

Use a separate fixture for bench GPIO control:

```python
from klab_pytest_toolkit_embedded.gpio_controllers import FtdiGpioController

@pytest.fixture
def gpio() -> FtdiGpioController:
    return FtdiGpioController(
        url="ftdi://ftdi:232h:1/1",
        pins={
            "reset_n": 0,
            "boot0": 1,
        },
    )


def test_boot_mode(dut: Board, gpio: FtdiGpioController):
    gpio.set_high("boot0")
    gpio.pulse("reset_n", 0.05)
```

### SPI Controller

Use a separate fixture for bench SPI access:

```python
from klab_pytest_toolkit_embedded.spi_controllers import FtdiSpiController, SpidevSpiController

@pytest.fixture
def spi() -> FtdiSpiController:
    return FtdiSpiController(
        url="ftdi://ftdi:232h:1/1",
        chip_select=0,
        frequency_hz=1_000_000,
        mode=0,
    )


def test_spi_flash_id(spi: FtdiSpiController):
    response = spi.transfer(b"\x9F\x00\x00\x00")
    assert len(response) == 4


@pytest.fixture
def linux_spi() -> SpidevSpiController:
    return SpidevSpiController(bus=0, device=0, max_speed_hz=1_000_000, mode=0)
```

### I2C Controller

Use a separate fixture for bench I2C access:

```python
from klab_pytest_toolkit_embedded.i2c_controllers import FtdiI2cController, SmbusI2cController

@pytest.fixture
def i2c() -> FtdiI2cController:
    return FtdiI2cController(
        url="ftdi://ftdi:232h:1/1",
        frequency_hz=400_000,
    )


def test_i2c_sensor_read(i2c: FtdiI2cController):
    i2c.write(0x48, b"\x00")
    data = i2c.read(0x48, 2)
    assert len(data) == 2


@pytest.fixture
def linux_i2c() -> SmbusI2cController:
    return SmbusI2cController(bus=1)
```

### Logic Analyzer

Use a separate fixture for bench equipment such as a logic analyzer:

```python
from klab_pytest_toolkit_embedded.logic_analyzers import SaleaeLogicAnalyzer

@pytest.fixture
def logic() -> SaleaeLogicAnalyzer:
    return SaleaeLogicAnalyzer(
        digital_channels={
            "spi_mosi": 0,
            "spi_miso": 1,
            "spi_clk": 2,
            "reset_n": 3,
        },
        sample_rate_hz=25_000_000,
        capture_seconds=2.0,
    )


def test_spi_boot_sequence(dut: Board, logic: SaleaeLogicAnalyzer):
    logic.start_capture()
    dut.reset()
    logic.stop_capture()

    capture = logic.get_capture()
    capture.export("artifacts/spi_boot.sal")
    capture.assert_has_channels("spi_clk", "reset_n")

    assert capture.channel("spi_clk") == 2
```

So yes: with `SaleaeLogicAnalyzer` you can pass channel names directly in the constructor instead of raw channel numbers in test code, and access the finished session through `logic.get_capture()`.

Current base `LogicCapture` helpers:
- `has_channel(name)`
- `assert_has_channel(name)`
- `assert_has_channels(*names)`
- `assert_any_activity(name)`
- `assert_no_activity(name)`
- `assert_toggles_at_least(name, count)`

Note: `SaleaeLogicCapture` currently supports channel-aware capture/export, but transition analysis is not implemented yet.

To use `SaleaeLogicAnalyzer`, install the optional Saleae dependency:

```bash
pip install 'klab-pytest-toolkit-embedded[saleae]'
```

## Examples

See the test files for comprehensive examples.

## Best Practices

### Keep DUT and Bench Fixtures Separate

Use `Board` for the device under test, and keep bench tools such as GPIO, SPI, I2C, and logic analyzers as separate fixtures:

```python
@pytest.fixture
def dut() -> Board:
    return Board(
        debug_probe=OpenOcdProbe(config_files=("board/st_nucleo_f4.cfg",)),
        communicator=SerialCommunicator(port="/dev/ttyACM0", baudrate=115200),
    )


@pytest.fixture
def gpio() -> FtdiGpioController:
    return FtdiGpioController(
        url="ftdi://ftdi:232h:1/1",
        pins={"reset_n": 0, "boot0": 1},
    )
```

This keeps test dependencies explicit and avoids turning `Board` into a large test-bench container.

### Prefer Named Pins and Channels

Use descriptive names for pins, buses, and logic-analyzer channels instead of raw indices inside tests:

```python
pins={"reset_n": 0, "boot0": 1}
digital_channels={"spi_clk": 0, "spi_mosi": 1, "reset_n": 2}
```

This makes tests easier to read and maintain.

### Keep Hardware Configuration Centralized

Keep serial ports, OpenOCD configs, bus numbers, chip-select values, and pin mappings in one place such as `conftest.py` or a dedicated configuration module.

### Choose the Right Backend

- Use Linux-native backends such as `SpidevSpiController` and `SmbusI2cController` when pytest runs directly on a Linux or Raspberry Pi bench.
- Use FTDI backends when the host does not expose native buses, or when you need a USB-connected bridge.
- Use `OpenOcdProbe` when you want broad probe/target flexibility.
- Use `ProbeRsProbe` when you want a modern ARM-focused flashing workflow.

### Use Context Managers

The `Board` class supports context managers to ensure proper cleanup of resources:

```python
with Board(debug_probe=debug_probe, communicator=communicator) as board:
    board.program(firmware_file)
    board.wait_for_regex_in_line(b"Ready", timeout_s=10)
    # Resources are automatically closed when exiting the context
```

### Timeout Configuration

When waiting for messages from the device, always specify appropriate timeouts to prevent tests from hanging:

```python
# Wait with custom timeout
dut.wait_for_regex_in_line(
    regex=b"Boot complete",
    timeout_s=30,
    log=True  # Enable logging to see device output
)
```

### Capture Artifacts for Debugging

For flaky or timing-sensitive tests, save useful artifacts such as UART logs and logic-analyzer captures so failures can be inspected later.

### Hardware Availability

For tests that require physical hardware, use `pytest.mark.skipif` to conditionally skip tests when hardware is not available:

```python
@pytest.mark.skipif(
    not hardware_available(),
    reason="This test requires a physical ESP32 device connected."
)
def test_with_hardware(dut: Board):
    # Test code here
    pass
```

## Links

- [Source code](https://github.com/klab365/klab-pytest-toolkit/tree/main/packages/klab-pytest-toolkit-embedded)
- [PyPI](https://pypi.org/project/klab-pytest-toolkit-embedded/)
- [Issue tracker](https://github.com/klab365/klab-pytest-toolkit/issues)

## License

MIT
