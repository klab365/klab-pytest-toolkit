"""Shared fixtures for the web package test suite.

Provides:

* ``playwright_browser`` — a session-scoped Chromium instance. Reusing one
  browser across the whole test session avoids paying the ~1–2s launch cost
  per test. Tests get isolation through per-test browser contexts.

* ``web_client`` — a function-scoped ``PlayWrightWebClient`` that yields a
  ready-to-use client backed by the shared browser. Most tests should
  request this fixture rather than calling
  ``web_client_factory.create_client(...)`` directly.

Tests that specifically want to exercise the factory's default-launch
behavior should still call ``web_client_factory.create_client()`` directly
without this fixture.
"""

from typing import Iterator

import pytest


@pytest.fixture(scope="session")
def playwright_browser() -> Iterator["object"]:
    """Launch a single Chromium browser for the entire test session."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            yield browser
        finally:
            browser.close()


@pytest.fixture
def web_client(web_client_factory, playwright_browser) -> Iterator["object"]:
    """Provide a ready-to-use Playwright web client backed by the shared browser.

    Each test gets its own context and page, so cookies/storage are isolated.
    The browser itself is shared across tests for speed.
    """
    client = web_client_factory.create_client(browser=playwright_browser)
    try:
        yield client
    finally:
        client.close()
