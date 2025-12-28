# Klab Pytest Toolkit - Embedded

Custom pytest fixtures for embedded systems testing.
The goal is to allow testers to easily test embedded devices with reusable components for programming, resetting, and communicating with boards.

At the moment the package provides the following components:

- `Board`: Main orchestration class for managing board operations, including programming, resetting, and communication.
- Debug Probes:
  - `EspTool`: Debug probe implementation for ESP32 devices using esptool.
- Communicators:
  - `SerialCommunicator`: Serial port communication interface for UART/USB connections.

## Installation

```bash
pip install klab-pytest-toolkit-embedded
```

## Usage

### Board Class

The `Board` class orchestrates board operations by combining a debug probe (for programming and resetting) with a communicator (for sending and receiving data).

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

## Examples

See the test files for comprehensive examples.

## Best Practices

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

## License

MIT
