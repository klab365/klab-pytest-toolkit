"""Unit tests for the Board class."""

from unittest.mock import patch

import pytest

from klab_pytest_toolkit_embedded.board import Board
from klab_pytest_toolkit_embedded.communicators import CommunicatorInterface
from klab_pytest_toolkit_embedded.debug_probes import DebugProbe


# Mock implementations for abstract classes
class MockDebugProbe(DebugProbe):
    """Mock implementation of DebugProbe for testing."""

    def __init__(self):
        self.programmed_images = []
        self.reset_count = 0
        self.closed = False

    def program(self, fw_image: str) -> None:
        """Mock program implementation."""
        self.programmed_images.append(fw_image)

    def reset(self) -> None:
        """Mock reset implementation."""
        self.reset_count += 1

    def close(self) -> None:
        """Mock close implementation."""
        self.closed = True


class MockCommunicator(CommunicatorInterface):
    """Mock implementation of CommunicatorInterface for testing."""

    def __init__(self):
        self.sent_data = []
        self.receive_buffer = b""
        self.closed = False

    def send(self, data: bytes) -> None:
        """Mock send implementation."""
        self.sent_data.append(data)

    def receive(self, num_bytes: int) -> bytes:
        """Mock receive implementation."""
        if len(self.receive_buffer) >= num_bytes:
            data = self.receive_buffer[:num_bytes]
            self.receive_buffer = self.receive_buffer[num_bytes:]
            return data
        else:
            data = self.receive_buffer
            self.receive_buffer = b""
            return data

    def close(self) -> None:
        """Mock close implementation."""
        self.closed = True

    def add_to_buffer(self, data: bytes) -> None:
        """Helper method to add data to receive buffer."""
        self.receive_buffer += data


# Fixtures
@pytest.fixture
def mock_debug_probe():
    """Fixture providing a mock debug probe."""
    return MockDebugProbe()


@pytest.fixture
def mock_communicator():
    """Fixture providing a mock communicator."""
    return MockCommunicator()


@pytest.fixture
def board(mock_debug_probe, mock_communicator):
    """Fixture providing a Board instance with mock dependencies."""
    return Board(debug_probe=mock_debug_probe, communicator=mock_communicator)


# Tests for Board initialization
def test_board_initialization(mock_debug_probe, mock_communicator):
    """Test that Board initializes with debug probe and communicator."""
    board = Board(debug_probe=mock_debug_probe, communicator=mock_communicator)
    assert board._debug_probe is mock_debug_probe
    assert board._communicator is mock_communicator


# Tests for Board programming functionality
def test_program_calls_debug_probe(board, mock_debug_probe):
    """Test that program() delegates to debug probe."""
    fw_image = "/path/to/firmware.bin"
    board.program(fw_image)
    assert fw_image in mock_debug_probe.programmed_images


def test_program_with_multiple_images(board, mock_debug_probe):
    """Test programming with multiple firmware images."""
    images = ["/path/to/fw1.bin", "/path/to/fw2.bin", "/path/to/fw3.bin"]
    for img in images:
        board.program(img)
    assert mock_debug_probe.programmed_images == images


# Tests for Board reset functionality
def test_reset_calls_debug_probe(board, mock_debug_probe):
    """Test that reset() delegates to debug probe."""
    board.reset()
    assert mock_debug_probe.reset_count == 1


def test_multiple_resets(board, mock_debug_probe):
    """Test multiple reset operations."""
    for _ in range(5):
        board.reset()
    assert mock_debug_probe.reset_count == 5


# Tests for Board communication functionality
def test_send_data(board, mock_communicator):
    """Test sending data through the communicator."""
    data = b"Hello, Board!"
    board.send(data)
    assert data in mock_communicator.sent_data


def test_send_multiple_messages(board, mock_communicator):
    """Test sending multiple messages."""
    messages = [b"msg1", b"msg2", b"msg3"]
    for msg in messages:
        board.send(msg)
    assert mock_communicator.sent_data == messages


def test_receive_some_default_size(board, mock_communicator):
    """Test receiving data with default size."""
    test_data = b"Test data from device"
    mock_communicator.add_to_buffer(test_data)
    received = board.receive_some()
    assert received == test_data


def test_receive_some_with_specific_size(board, mock_communicator):
    """Test receiving specific number of bytes."""
    test_data = b"A" * 100
    mock_communicator.add_to_buffer(test_data)
    received = board.receive_some(num_bytes=50)
    assert len(received) == 50
    assert received == b"A" * 50


def test_receive_some_empty_buffer(board, mock_communicator):
    """Test receiving from empty buffer."""
    received = board.receive_some(num_bytes=10)
    assert received == b""


# Tests for wait_for_regex_in_line functionality
def test_wait_for_regex_immediate_match(board, mock_communicator):
    """Test regex matching when data is immediately available."""
    test_data = b"System initialized\nReady to proceed\n"
    mock_communicator.add_to_buffer(test_data)
    result = board.wait_for_regex_in_line(r"Ready to proceed", timeout_s=5, log=False)
    assert result is True


def test_wait_for_regex_partial_match(board, mock_communicator):
    """Test regex matching with pattern."""
    test_data = b"Temperature: 25.5C\nPressure: 1013hPa\n"
    mock_communicator.add_to_buffer(test_data)
    result = board.wait_for_regex_in_line(r"Temperature: \d+\.\d+", timeout_s=5, log=False)
    assert result is True


def test_wait_for_regex_multiline(board, mock_communicator):
    """Test regex matching across multiple lines."""
    test_data = b"Line 1\nLine 2\nTarget line found\nLine 4\n"
    mock_communicator.add_to_buffer(test_data)
    result = board.wait_for_regex_in_line(r"Target line", timeout_s=5, log=False)
    assert result is True


def test_wait_for_regex_with_carriage_return(board, mock_communicator):
    """Test regex matching with carriage return characters."""
    test_data = b"Loading...\r\nComplete!\r\n"
    mock_communicator.add_to_buffer(test_data)
    result = board.wait_for_regex_in_line(r"Complete!", timeout_s=5, log=False)
    assert result is True


def test_wait_for_regex_timeout(board, mock_communicator):
    """Test that timeout raises TimeoutError."""
    test_data = b"No match here\n"
    mock_communicator.add_to_buffer(test_data)
    with pytest.raises(TimeoutError, match=r"Timeout waiting for regex"):
        board.wait_for_regex_in_line(r"NonExistentPattern", timeout_s=1, log=False)


def test_wait_for_regex_incremental_data(board, mock_communicator):
    """Test regex matching with incrementally added data."""
    # Add data in chunks to simulate real-world scenario
    mock_communicator.add_to_buffer(b"Starting process\n")
    mock_communicator.add_to_buffer(b"Processing...\n")
    mock_communicator.add_to_buffer(b"Success!\n")
    result = board.wait_for_regex_in_line(r"Success", timeout_s=5, log=False)
    assert result is True


def test_wait_for_regex_unicode_handling(board, mock_communicator):
    """Test regex matching with UTF-8 encoded data."""
    test_data = "Status: ✓ OK\n".encode("utf-8")
    mock_communicator.add_to_buffer(test_data)
    result = board.wait_for_regex_in_line(r"Status:.*OK", timeout_s=5, log=False)
    assert result is True


@patch("builtins.print")
def test_wait_for_regex_with_logging(mock_print, board, mock_communicator):
    """Test that logging works when enabled."""
    test_data = b"Log this message\n"
    mock_communicator.add_to_buffer(test_data)
    board.wait_for_regex_in_line(r"Log this", timeout_s=5, log=True)
    # Verify print was called
    mock_print.assert_called()


# Tests for Board context manager functionality
def test_context_manager_enter(board):
    """Test context manager __enter__ returns self."""
    with board as b:
        assert b is board


def test_context_manager_exit_closes_connections(mock_debug_probe, mock_communicator):
    """Test context manager __exit__ closes both probe and communicator."""
    board = Board(debug_probe=mock_debug_probe, communicator=mock_communicator)
    with board:
        pass
    assert mock_communicator.closed is True
    assert mock_debug_probe.closed is True


def test_context_manager_exit_on_exception(mock_debug_probe, mock_communicator):
    """Test context manager closes connections even on exception."""
    board = Board(debug_probe=mock_debug_probe, communicator=mock_communicator)
    try:
        with board:
            raise ValueError("Test exception")
    except ValueError:
        pass
    assert mock_communicator.closed is True
    assert mock_debug_probe.closed is True


# Integration tests for Board operations
def test_complete_workflow(board, mock_debug_probe, mock_communicator):
    """Test a complete board workflow: program, reset, send, receive."""
    # Program firmware
    fw_image = "/path/to/firmware.bin"
    board.program(fw_image)
    assert fw_image in mock_debug_probe.programmed_images

    # Reset board
    board.reset()
    assert mock_debug_probe.reset_count == 1

    # Send command
    command = b"START\n"
    board.send(command)
    assert command in mock_communicator.sent_data

    # Receive response
    mock_communicator.add_to_buffer(b"OK\n")
    response = board.receive_some(num_bytes=10)
    assert response == b"OK\n"


def test_board_as_context_manager_workflow(mock_debug_probe, mock_communicator):
    """Test using Board as context manager with complete workflow."""
    with Board(debug_probe=mock_debug_probe, communicator=mock_communicator) as board:
        board.program("/firmware.bin")
        board.reset()
        board.send(b"TEST")
        mock_communicator.add_to_buffer(b"RESPONSE")
        data = board.receive_some()
        assert data == b"RESPONSE"

    assert mock_communicator.closed is True
    assert mock_debug_probe.closed is True


# Edge case tests
def test_empty_firmware_path(board, mock_debug_probe):
    """Test programming with empty firmware path."""
    board.program("")
    assert "" in mock_debug_probe.programmed_images


def test_send_empty_data(board, mock_communicator):
    """Test sending empty data."""
    board.send(b"")
    assert b"" in mock_communicator.sent_data


def test_receive_zero_bytes(board, mock_communicator):
    """Test receiving zero bytes."""
    mock_communicator.add_to_buffer(b"data")
    received = board.receive_some(num_bytes=0)
    assert received == b""


def test_wait_for_regex_empty_string(board, mock_communicator):
    """Test waiting for empty regex pattern."""
    mock_communicator.add_to_buffer(b"Some data\n")
    # Empty pattern should match
    result = board.wait_for_regex_in_line(r"", timeout_s=1, log=False)
    assert result is True
