# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

#### klab-pytest-toolkit-webfixtures
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
