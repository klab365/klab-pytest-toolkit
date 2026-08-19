FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04 AS dev

SHELL ["/bin/bash", "-euo", "pipefail", "-c"]

# This Dockerfile is intentionally minimal. OS-level test dependencies
# are managed by mise's [bootstrap.packages] section in mise.toml —
# the single source of truth shared by local dev, CI, and this dev
# container. They are applied at container start via ``postStartCommand``
# in devcontainer.json, so we don't bake them into the image.

# Devcontainer-only setup: give the non-root `vscode` user access to
# serial ports so embedded tests can talk to /dev/ttyUSB0 hardware.
RUN usermod -a -G dialout vscode
