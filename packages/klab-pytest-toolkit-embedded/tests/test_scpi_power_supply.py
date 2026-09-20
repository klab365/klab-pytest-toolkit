"""Tests for the SCPI power supply adapter."""

import pytest

from klab_pytest_toolkit_embedded.communicators import CommunicatorInterface
from klab_pytest_toolkit_embedded.measurements import (
    Current,
    CurrentUnit,
    ScpiPowerSupply,
    Voltage,
    VoltageUnit,
)


class FakeCommunicator(CommunicatorInterface):
    """A scripted communicator for testing."""

    def __init__(self, responses: dict[str, str]) -> None:
        self._responses = responses
        self.sent: list[str] = []
        self.closed = False

    def send(self, data: bytes) -> None:
        self.sent.append(data.decode().strip())

    def receive(self, num_bytes: int) -> bytes:
        return b""

    def read_line(self) -> bytes:
        return self._responses[self.sent[-1]].encode()

    def close(self) -> None:
        self.closed = True


def make_supply() -> tuple[ScpiPowerSupply, FakeCommunicator]:
    communicator = FakeCommunicator(
        {
            "MEASure:VOLTage?": "+3.30000000E+00",
            "MEASure:CURRent?": "+1.25000000E-03",
        }
    )
    return ScpiPowerSupply(communicator), communicator


def test_set_voltage_writes_base_unit() -> None:
    supply, communicator = make_supply()

    supply.set_voltage(Voltage(3.3, VoltageUnit.VOLT))

    assert communicator.sent == ["VOLTage 3.3"]


def test_set_voltage_converts_to_volts() -> None:
    supply, communicator = make_supply()

    supply.set_voltage(Voltage(3300, VoltageUnit.MILLIVOLT))

    assert communicator.sent == ["VOLTage 3.3"]


def test_set_current_limit_writes_base_unit() -> None:
    supply, communicator = make_supply()

    supply.set_current_limit(Current(500, CurrentUnit.MILLIAMPERE))

    assert communicator.sent == ["CURRent 0.5"]


def test_enable_and_disable_output() -> None:
    supply, communicator = make_supply()

    supply.enable_output()
    supply.disable_output()

    assert communicator.sent == ["OUTPut ON", "OUTPut OFF"]


def test_measure_voltage_and_current() -> None:
    supply, _ = make_supply()

    voltage = supply.measure_voltage()
    current = supply.measure_current()

    assert voltage.unit is VoltageUnit.VOLT
    assert voltage.value == pytest.approx(3.3)
    assert current.to(CurrentUnit.MILLIAMPERE).value == pytest.approx(1.25)


def test_context_manager_disables_output_and_closes() -> None:
    supply, communicator = make_supply()

    with supply:
        supply.enable_output()

    assert communicator.sent == ["OUTPut ON", "OUTPut OFF"]
    assert communicator.closed is True


def test_context_manager_disables_output_on_error() -> None:
    supply, communicator = make_supply()

    with pytest.raises(RuntimeError, match="boom"):
        with supply:
            raise RuntimeError("boom")

    assert communicator.sent == ["OUTPut OFF"]
    assert communicator.closed is True
