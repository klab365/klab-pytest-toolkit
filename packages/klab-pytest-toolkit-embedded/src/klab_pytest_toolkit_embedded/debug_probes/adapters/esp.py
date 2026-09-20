from klab_pytest_toolkit_embedded.debug_probes.interface import DebugProbe

import esptool


class EspTool(DebugProbe):
    """ESP debug probe using esptool.py."""

    def __init__(self, port: str, baudrate: int = 1500000, address: str = "0x0"):
        self._port = port
        self._baudrate = baudrate
        self._address = address

    def program(self, fw_image: str) -> None:
        cmd = [
            "--chip",
            "esp32",
            "--port",
            self._port,
            "--baud",
            str(self._baudrate),
            "--after",
            "hard_reset",
            "write_flash",
            "-e",
            self._address,
            fw_image,
        ]

        esptool.main(cmd)

    def reset(self) -> None:
        cmd = [
            "--chip",
            "esp32",
            "--port",
            self._port,
            "--baud",
            str(self._baudrate),
            "reset",
        ]

        esptool.main(cmd)

    def close(self) -> None:
        """Close the debug probe connection."""
        # esptool does not maintain a persistent connection, so nothing to close.
        pass
