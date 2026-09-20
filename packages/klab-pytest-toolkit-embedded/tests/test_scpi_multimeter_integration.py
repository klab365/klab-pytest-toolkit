"""End-to-end test of ScpiMultimeter against a local SCPI simulator."""

import socket
import threading
from collections.abc import Iterator

import pytest

from klab_pytest_toolkit_embedded.communicators import TcpCommunicator
from klab_pytest_toolkit_embedded.measurements import (
    CurrentUnit,
    ScpiMultimeter,
    VoltageUnit,
)


class ScpiSimulator:
    """A minimal threaded TCP server that speaks a tiny subset of SCPI."""

    def __init__(self, responses: dict[str, str]) -> None:
        self._responses = responses
        self._server = socket.socket()
        self._server.bind(("127.0.0.1", 0))
        self._server.listen(1)
        self.port = self._server.getsockname()[1]
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self) -> None:
        self._thread.start()

    def _run(self) -> None:
        conn, _ = self._server.accept()
        with conn:
            reader = conn.makefile("rb")
            while True:
                line = reader.readline()
                if not line:
                    break
                command = line.decode().strip()
                response = self._responses.get(command)
                if response is not None:
                    conn.sendall(f"{response}\n".encode())
        self._server.close()

    def close(self) -> None:
        self._server.close()


@pytest.fixture
def simulator() -> Iterator[ScpiSimulator]:
    sim = ScpiSimulator(
        {
            "*IDN?": "Keysight,34465A",
            "MEASure:VOLTage:DC?": "+3.30000000E+00",
            "MEASure:CURRent:DC?": "+1.25000000E-03",
        }
    )
    sim.start()
    yield sim
    sim.close()


def test_measurements_over_real_tcp_socket(simulator: ScpiSimulator) -> None:
    communicator = TcpCommunicator(host="127.0.0.1", port=simulator.port)

    with ScpiMultimeter(communicator) as meter:
        assert meter.identify() == "Keysight,34465A"
        voltage = meter.measure_voltage()
        current = meter.measure_current()

    assert voltage.unit is VoltageUnit.VOLT
    assert voltage.value == pytest.approx(3.3)
    assert current.to(CurrentUnit.MILLIAMPERE).value == pytest.approx(1.25)
