# klab-pytest-toolkit

This repo contains a collection of utilities and tools to enhance the experience of using `pytest` for system testing.
The goal is to provide reusable components that can be easily use for different type of projects.
The purpose is not to test only python projects. 
The toolkit can be used to test any type of system, regardless of the implementation language.
The toolkit dont aim to replace or force to a specific pattern. It is a extension to pytest to provide useful fixtures and decorators to make the test writing easier and more consistent.

## Overview

The toolkit includes the following components:

| Package                                                                     | Description                                                                            |
| --------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| [klab-pytest-toolkit-decorators](./packages/klab-pytest-toolkit-decorators) | Custom pytest decorators for marking and annotating tests                              |
| [klab-pytest-toolkit-prompt](./packages/klab-pytest-toolkit-prompt)         | Interactive user prompts during test execution using tkinter UI dialogs                |
| [klab-pytest-toolkit-web](./packages/klab-pytest-toolkit-web)               | Web testing fixtures with JSON validation, REST API client, and Playwright integration |

### Architecture

Each package is designed for a specific type of application testing needed.
When the package has fixtures, then they are available with factories to create different variants of the fixture.

## Development

The project use `uv` and Docker for development environment management.
The development environment can be started with vscode and devcontainers.
Each command is abstracted in the `Justfile` for ease of use.

Here are some common commands:

- `just check-format`: Check code formatting
- `just format`: Format the code
- `just lint`: Lint the code
- `just test`: Run the tests