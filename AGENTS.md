# AGENTS.md

## Project overview

`klab-pytest-toolkit` is a `uv` workspace containing independently published pytest-plugin packages:

- `packages/klab-pytest-toolkit-decorators` — pytest marks and decorators.
- `packages/klab-pytest-toolkit-embedded` — embedded, HIL, and Linux/FTDI fixtures.
- `packages/klab-pytest-toolkit-prompt` — tkinter-based interactive prompts.
- `packages/klab-pytest-toolkit-web` — REST, gRPC, JSON-validation, and Playwright fixtures.

Each package uses the `src/` layout, has its own `pyproject.toml`, README, tests, and pytest entry point. Package versions are dynamic and sourced from `src/<package_module>/__init__.py`.

## Environment and dependencies

- Use Python and dependencies through `mise` and `uv`; do not invoke a system Python or `pip` directly.
- Install the configured toolchain with `mise install`. Its post-install hook installs Chromium and required OS packages.
- The root `pyproject.toml` defines the `uv` workspace and shared pytest configuration. Keep `uv.lock` in sync when dependency definitions change.
- Playwright browsers are stored in `.ms-playwright/` via `PLAYWRIGHT_BROWSERS_PATH`.
- Never commit generated caches, coverage reports, package build output, or local secrets from `.env`.

## Development commands

Run commands from the repository root:

```bash
mise run check-format                 # Ruff lint + formatting check
mise run format                       # format and apply safe Ruff fixes
mise run lint                         # ty type check + Ruff lint
mise run test                         # entire suite under Xvfb with coverage
mise run test -- packages/<package>   # targeted package test run
mise run build                        # build all distributions into dist/
mise run clean                        # remove generated test/build artifacts
```

For quick focused work, use `uv run pytest <test path>`; use `mise run test` before finishing changes that may require tkinter or Playwright, since it runs under `xvfb-run` and produces coverage/JUnit reports.

The default pytest configuration excludes `packages/klab-pytest-toolkit-embedded/tests/test_esp32_hardware.py`, because it requires a physical ESP32 at `/dev/ttyUSB0`. Run it explicitly only when the required hardware is connected.

## Code and test conventions

- Target Python 3.13 formatting rules; packages support Python 3.11+.
- Follow Ruff configuration: 4-space indentation, double-quoted strings, and a 100-character line limit.
- Add type annotations and concise docstrings consistent with nearby code.
- Keep implementation under `packages/<distribution>/src/<import_module>/` and tests under its sibling `tests/` directory.
- Name tests `test_*.py` and test functions `test_*`. Use pytest fixtures for setup and teardown; keep tests deterministic and clean up external resources.
- Prefer fakes/mocks or containerized services for external integrations. Do not make ordinary tests depend on physical hardware, a GUI display, or live network services.
- When changing a fixture or plugin API, update the package README and add/adjust tests in the same package.
- Preserve package pytest entry points (`[project.entry-points.pytest11]`) when refactoring plugin modules.

## Validation expectations

1. Run focused tests for every affected package.
2. Run `mise run check-format` and `mise run lint` for Python changes.
3. Run `mise run test` for cross-package, UI, Playwright, or plugin-registration changes when the environment supports it.
4. Run `mise run build` after packaging metadata, entry-point, dependency, or version changes.

## Releases

Use `mise run update-version <version>` to update every package version together. Build with `mise run build`; publishing requires `PYPI_TOKEN` and is performed by `mise run publish <token>`. Do not publish or alter versions unless explicitly requested.
