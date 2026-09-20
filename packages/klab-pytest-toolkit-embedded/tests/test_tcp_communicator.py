"""Tests for the TCP communicator."""

from unittest.mock import MagicMock, patch

from klab_pytest_toolkit_embedded.communicators import TcpCommunicator


def make_socket() -> MagicMock:
    socket = MagicMock()
    socket.recv.side_effect = [b"1.23\n", b""]
    return socket


def test_send_delegates_to_socket() -> None:
    mock_socket = MagicMock()
    with patch("socket.create_connection", return_value=mock_socket):
        communicator = TcpCommunicator("10.0.0.5", 5025)

        communicator.send(b"*RST\n")

    mock_socket.sendall.assert_called_once_with(b"*RST\n")


def test_receive_delegates_to_socket() -> None:
    mock_socket = MagicMock()
    mock_socket.recv.return_value = b"abc"
    with patch("socket.create_connection", return_value=mock_socket):
        communicator = TcpCommunicator("10.0.0.5", 5025)

        assert communicator.receive(3) == b"abc"

    mock_socket.recv.assert_called_once_with(3)


def test_read_line_reads_until_newline() -> None:
    mock_socket = make_socket()
    with patch("socket.create_connection", return_value=mock_socket):
        communicator = TcpCommunicator("10.0.0.5", 5025)

        assert communicator.read_line() == b"1.23\n"


def test_close_closes_socket() -> None:
    mock_socket = MagicMock()
    with patch("socket.create_connection", return_value=mock_socket):
        communicator = TcpCommunicator("10.0.0.5", 5025)

        communicator.close()

    mock_socket.close.assert_called_once()


def test_context_manager_closes_on_exit() -> None:
    mock_socket = make_socket()
    with patch("socket.create_connection", return_value=mock_socket):
        with TcpCommunicator("10.0.0.5", 5025) as communicator:
            assert communicator.read_line() == b"1.23\n"

    mock_socket.close.assert_called_once()
