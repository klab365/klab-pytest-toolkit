# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
