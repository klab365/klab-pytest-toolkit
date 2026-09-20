"""Tests for the serial communicator."""

from unittest.mock import MagicMock, patch

from klab_pytest_toolkit_embedded.communicators import SerialCommunicator


def make_serial() -> MagicMock:
    serial = MagicMock()
    serial.is_open = True
    serial.readline.return_value = b"1.23\r\n"
    return serial


def test_send_writes_and_flushes() -> None:
    mock_serial = make_serial()
    with patch("serial.Serial", return_value=mock_serial):
        communicator = SerialCommunicator("/dev/ttyUSB0")

        communicator.send(b"*RST\n")

    mock_serial.write.assert_called_once_with(b"*RST\n")
    mock_serial.flush.assert_called_once()


def test_receive_reads_requested_bytes() -> None:
    mock_serial = make_serial()
    mock_serial.read.return_value = b"abc"
    with patch("serial.Serial", return_value=mock_serial):
        communicator = SerialCommunicator("/dev/ttyUSB0")

        assert communicator.receive(3) == b"abc"

    mock_serial.read.assert_called_once_with(3)


def test_read_line_delegates_to_pyserial() -> None:
    mock_serial = make_serial()
    with patch("serial.Serial", return_value=mock_serial):
        communicator = SerialCommunicator("/dev/ttyUSB0")

        assert communicator.read_line() == b"1.23\r\n"

    mock_serial.readline.assert_called_once()


def test_close_closes_serial_connection() -> None:
    mock_serial = make_serial()
    with patch("serial.Serial", return_value=mock_serial):
        communicator = SerialCommunicator("/dev/ttyUSB0")

        communicator.close()

    mock_serial.close.assert_called_once()
