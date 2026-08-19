# klab-pytest-toolkit

A collection of utilities and tools to enhance the experience of using `pytest` for system testing.

The goal is to provide reusable components that can be easily used across different types of projects.
The toolkit is **not** limited to testing Python projects — it can be used to test any system, regardless of the implementation language.
It does not aim to replace `pytest` or enforce a specific pattern. Instead, it extends `pytest` with useful fixtures and decorators to make test writing easier and more consistent.

## Overview

The toolkit includes the following components:

| Package                                                                                                              | Description                                                                            | PyPI                                                                                  |
| -------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| [`klab-pytest-toolkit-decorators`](./packages/klab-pytest-toolkit-decorators)                                        | Custom pytest decorators for marking and annotating tests                              | [![PyPI](https://img.shields.io/pypi/v/klab-pytest-toolkit-decorators)](https://pypi.org/project/klab-pytest-toolkit-decorators/) |
| [`klab-pytest-toolkit-embedded`](./packages/klab-pytest-toolkit-embedded)                                            | Pytest fixtures for embedded systems testing                                           | [![PyPI](https://img.shields.io/pypi/v/klab-pytest-toolkit-embedded)](https://pypi.org/project/klab-pytest-toolkit-embedded/)     |
| [`klab-pytest-toolkit-prompt`](./packages/klab-pytest-toolkit-prompt)                                                | Interactive user prompts during test execution using tkinter UI dialogs                | [![PyPI](https://img.shields.io/pypi/v/klab-pytest-toolkit-prompt)](https://pypi.org/project/klab-pytest-toolkit-prompt/)         |
| [`klab-pytest-toolkit-web`](./packages/klab-pytest-toolkit-web)                                                      | Web testing fixtures with JSON validation, REST API client, and Playwright integration | [![PyPI](https://img.shields.io/pypi/v/klab-pytest-toolkit-web)](https://pypi.org/project/klab-pytest-toolkit-web/)               |

### Architecture

Each package is designed for a specific type of application testing.
When a package exposes fixtures, they are provided with factories so different variants can be created easily.

## Development

The project uses [`uv`](https://github.com/astral-sh/uv) and Docker for development environment management.
The development environment can be started with VS Code and dev containers.
Each task is defined in [`mise.toml`](./mise.toml) and can be run with `mise run <task>`.

Here are some common tasks:

| Task                      | Description                                                              |
| ------------------------- | ------------------------------------------------------------------------ |
| `mise run check-format`   | Check if the code is formatted correctly                                 |
| `mise run format`         | Format the code with Ruff and apply auto-fixes                           |
| `mise run lint`           | Run type checking with `ty` and linting with `ruff`                       |
| `mise run test`           | Run pytest with coverage (`xvfb-run` is used for Playwright headless)    |
| `mise run clean`          | Remove caches, build artifacts, and coverage reports                     |
| `mise run build`          | Build all packages into `dist/`                                          |
| `mise run publish`        | Publish built distributions to PyPI (requires `PYPI_TOKEN`)              |
| `mise run update-version` | Update the `__version__` in every package to the supplied version string |

Examples:

```bash
mise run lint
mise run test -- packages/klab-pytest-toolkit-web
mise run update-version 1.2.3
```
