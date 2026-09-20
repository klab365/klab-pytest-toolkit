"""Tests for the VISA communicator."""

from unittest.mock import patch

import pytest

from klab_pytest_toolkit_embedded.communicators import VisaCommunicator


class FakeVisaBackend:
    """A scripted VISA backend for testing."""

    def __init__(self, resource_name: str) -> None:
        self.resource_name = resource_name
        self.written: list[bytes] = []
        self.closed = False
        self.read_response = "1.23"
        self.read_bytes_response = b""

    def write_raw(self, data: bytes) -> None:
        self.written.append(data)

    def read_bytes(self, count: int) -> bytes:
        return self.read_bytes_response

    def read(self) -> str:
        return self.read_response

    def close(self) -> None:
        self.closed = True


def make_communicator() -> tuple[VisaCommunicator, FakeVisaBackend]:
    backend = FakeVisaBackend("USB0::0x1234::0x5678::INSTR")
    communicator = VisaCommunicator(
        backend.resource_name,
        backend_factory=lambda name: backend,
    )
    return communicator, backend


def test_send_writes_raw_bytes() -> None:
    communicator, backend = make_communicator()

    communicator.send(b"*RST\n")

    assert backend.written == [b"*RST\n"]


def test_receive_reads_bytes() -> None:
    communicator, backend = make_communicator()
    backend.read_bytes_response = b"abc"

    assert communicator.receive(3) == b"abc"


def test_read_line_uses_termination_read() -> None:
    communicator, backend = make_communicator()

    assert communicator.read_line() == b"1.23"


def test_close_closes_backend() -> None:
    communicator, backend = make_communicator()

    communicator.close()

    assert backend.closed is True


def test_context_manager_closes_on_exit() -> None:
    communicator, backend = make_communicator()

    with communicator:
        pass

    assert backend.closed is True


def test_missing_pyvisa_raises_runtime_error() -> None:
    with patch(
        "klab_pytest_toolkit_embedded.communicators.adapters.visa.import_module",
        side_effect=ImportError("no pyvisa"),
    ):
        with pytest.raises(RuntimeError, match="visa"):
            VisaCommunicator("USB0::0x1234::0x5678::INSTR")
