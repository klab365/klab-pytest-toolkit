# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added

#### klab-pytest-toolkit-embedded
- Added asynchronous `BleClient` GATT support for characteristic reads, writes, and notifications,
  including optional connection-time pairing through the `ble` extra (`bleak`).

## 1.3.0

### Added

#### klab-pytest-toolkit-embedded
- Added unit-aware measurement value objects and unit conversions for current, voltage, resistance,
  frequency, and temperature.
- Added `MeasurementInstrument` and `PowerSupply` protocols for HIL measurement fixtures.
- Added SCPI instrument adapters: `ScpiMultimeter` for DC/AC voltage and current, resistance,
  frequency, and temperature measurements; and `ScpiPowerSupply` for output control and readings.
- Added `TcpCommunicator` for raw TCP/LXI device communication and `VisaCommunicator` for bench
  instruments, with a `visa` optional dependency extra that installs `pyvisa`.
- Added line-oriented reads to the communicator interface and serial implementation.

#### klab-pytest-toolkit-web
- Added a configurable 30-second default timeout for REST clients, with optional per-request
  overrides.

### Changed

#### klab-pytest-toolkit-embedded
- Reorganized concrete debug-probe, logic-analyzer, GPIO, SPI, I2C, and communicator implementations
  into `adapters` packages while preserving their parent-package public imports.
- Updated embedded documentation with direct-use guidance and TCP, VISA, SCPI multimeter, and power
  supply examples.

#### klab-pytest-toolkit-web
- Made dynamic gRPC proto-module loading collision-safe for multiple clients or matching user module
  names, and report missing request classes with warnings.
- Changed the Playwright web-client type to a string enum and made JSON-validator error handling
  explicitly default to returning `False`.
- Updated documentation to describe direct factory usage, REST timeout behavior, and current web-client
  APIs.

#### klab-pytest-toolkit-prompt
- Updated documentation to describe direct `PromptFactory` usage.

### Removed

#### klab-pytest-toolkit-embedded
- Removed automatic pytest-plugin registration and its fixtures; use the library classes directly or
  wrap them in project-owned fixtures.

#### klab-pytest-toolkit-prompt
- Removed automatic pytest-plugin registration and the `prompt_factory` fixture; use `PromptFactory`
  directly or wrap it in a project-owned fixture.

#### klab-pytest-toolkit-web
- Removed automatic pytest-plugin registration and the `response_validator_factory`,
  `api_client_factory`, and `web_client_factory` fixtures; use the factory classes directly or wrap
  them in project-owned fixtures.

### Development
- Updated the root documentation to clarify package roles and the direct factory pattern.
- Added contributor guidance in `AGENTS.md` and made the test task fall back to pytest directly when
  `xvfb-run` is unavailable.

## 1.2.0

### Added

#### klab-pytest-toolkit-embedded
- Added optional dependency groups for Saleae, FTDI, and Linux bench integrations
- Added `OpenOcdProbe` debug probe backend using the `openocd` CLI
- Added `ProbeRsProbe` debug probe backend using the `probe-rs` CLI
- Added `LogicAnalyzer` and `LogicCapture` abstractions for reusable bench capture workflows
- Added `SaleaeLogicAnalyzer` and `SaleaeLogicCapture` integrations for named-channel logic captures
- Added `GpioController`, `SpiController`, and `I2cController` abstractions for reusable bench bus control
- Added FTDI-based GPIO, SPI, and I2C controller implementations
- Added Linux-native `SpidevSpiController` and `SmbusI2cController` backends for SBC and bench-host workflows
- Added usage guidance and best-practice documentation for embedded HIL fixture design

### Changed

#### klab-pytest-toolkit-embedded
- Updated `Board` to support optional debug-probe and communicator dependencies
- Improved `Board.wait_for_regex_in_line()` to support `str`, `bytes`, and compiled regex patterns
- Improved cleanup and typing robustness across embedded controllers and analyzer backends

## 1.1.0

### Added

#### klab-pytest-toolkit-embedded
- Added initial structure for embedded testing toolkit
- Created `DebugProbe` abstract base class for debug probe implementations
- Created `CommunicatorInterface` abstract base class for communication interfaces
- Implemented `SerialCommunicator` for serial port communication
- Implemented `EspTool` debug probe for ESP32 devices

## 1.0.0

### Added

#### klab-pytest-toolkit-decorators
- Initial release
- `@requirement(id: str)` decorator for marking tests with requirement IDs
- Automatic junit XML output integration for requirement traceability
- Pytest plugin integration

#### klab-pytest-toolkit-prompt
- Initial release
- `ui_prompt_factory` fixture for creating interactive UI prompts
- Tkinter-based dialog system for user interaction during tests
- Support for confirmation prompts and information display
- `PromptInterface` and `PromptFactory` core classes
- Pytest plugin integration

#### klab-pytest-toolkit-web
- Initial release
- `response_validator_factory` fixture for JSON response validation
- `api_client_factory` fixture for creating REST API clients
- `web_client_factory` fixture for Playwright-based browser automation
- `JsonResponseValidator` with JSON schema validation support
- `RestApiClient` for HTTP requests with built-in validation
- `GrpcClient` for gRPC service interaction
- `WebClient` wrapper for Playwright browser testing
- Pytest plugin integration

### Infrastructure
- Automated CD pipeline for building and publishing to PyPI
- Monorepo structure with uv workspace support
- Docker-based development environment
- Just commands for build automation
- Comprehensive test coverage with pytest
- Code quality tools (ruff, ty)
