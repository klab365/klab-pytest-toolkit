"""Tests for WebClient using testcontainers with nginx."""

import os

import pytest
from testcontainers.core.container import DockerContainer

from klab_pytest_toolkit_web import WebClientFactory
from klab_pytest_toolkit_web.web_client import PlayWrightWebClient


# HTML content for testing
TEST_HTML_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
</head>
<body>
    <h1 id="main-heading">Welcome to Test Page</h1>
    <p id="description">This is a test page for web client testing.</p>

    <form id="test-form">
        <input type="text" id="username" name="username" placeholder="Username">
        <input type="password" id="password" name="password" placeholder="Password">
        <input type="email" id="email" name="email" placeholder="Email">
        <button type="submit" id="submit-btn">Submit</button>
    </form>

    <div id="content-section">
        <p class="paragraph">First paragraph</p>
        <p class="paragraph">Second paragraph</p>
        <p class="paragraph">Third paragraph</p>
    </div>

    <select id="dropdown">
        <option value="option1">Option 1</option>
        <option value="option2">Option 2</option>
        <option value="option3">Option 3</option>
    </select>

    <input type="checkbox" id="checkbox1" name="checkbox1">
    <label for="checkbox1">Checkbox 1</label>

    <input type="checkbox" id="checkbox2" name="checkbox2" checked>
    <label for="checkbox2">Checkbox 2</label>

    <a href="/about.html" id="about-link">About</a>

    <div id="hidden-element" style="display: none;">Hidden Content</div>

    <button id="disabled-btn" disabled>Disabled Button</button>
    <button id="enabled-btn">Enabled Button</button>

    <div id="text-content" data-testid="text-box">
        Some text content here
    </div>
</body>
</html>
"""

ABOUT_HTML_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>About Page</title>
</head>
<body>
    <h1 id="about-heading">About Us</h1>
    <p>This is the about page.</p>
    <a href="/index.html" id="home-link">Back to Home</a>
</body>
</html>
"""


@pytest.fixture(scope="session")
def nginx_container():
    """Fixture to provide an nginx container serving test HTML files."""
    with DockerContainer("nginx:alpine") as nginx:
        nginx.with_exposed_ports(80)
        nginx.start()

        # Write HTML files directly into the container
        container = nginx.get_wrapped_container()
        container.exec_run(
            [
                "sh",
                "-c",
                f"cat > /usr/share/nginx/html/index.html << 'EOF'\n{TEST_HTML_CONTENT}\nEOF",
            ]
        )
        container.exec_run(
            [
                "sh",
                "-c",
                f"cat > /usr/share/nginx/html/about.html << 'EOF'\n{ABOUT_HTML_CONTENT}\nEOF",
            ]
        )

        port = nginx.get_exposed_port(80)
        base_url = f"http://localhost:{port}"
        yield base_url


# Navigation tests


def test_navigate_to(web_client, nginx_container: str):
    """Test navigating to a URL."""
    web_client.navigate_to(f"{nginx_container}/index.html")
    assert "Test Page" in web_client.get_title()


def test_get_url(web_client, nginx_container: str):
    """Test getting current URL."""
    web_client.navigate_to(f"{nginx_container}/index.html")
    assert nginx_container in web_client.get_url()
    assert "index.html" in web_client.get_url()


def test_get_title(web_client, nginx_container: str):
    """Test getting page title."""
    web_client.navigate_to(f"{nginx_container}/index.html")
    assert web_client.get_title() == "Test Page"


# Element interaction tests


def test_click(web_client, nginx_container: str):
    """Test clicking on an element."""
    web_client.navigate_to(f"{nginx_container}/index.html")
    web_client.click("#about-link")
    assert "about.html" in web_client.get_url()
    assert "About Page" in web_client.get_title()


def test_fill(web_client, nginx_container: str):
    """Test filling a form field."""
    web_client.navigate_to(f"{nginx_container}/index.html")

    web_client.fill("#username", "testuser")
    web_client.fill("#password", "testpass")
    web_client.fill("#email", "test@example.com")

    assert web_client.get_input_value("#username") == "testuser"
    assert web_client.get_input_value("#password") == "testpass"
    assert web_client.get_input_value("#email") == "test@example.com"


def test_select_option(web_client, nginx_container: str):
    """Test selecting an option from a dropdown."""
    web_client.navigate_to(f"{nginx_container}/index.html")
    web_client.select_option("#dropdown", "option2")

    selected_value = web_client.get_input_value("#dropdown")
    assert selected_value == "option2"


def test_check_checkbox(web_client, nginx_container: str):
    """Test checking a checkbox."""
    web_client.navigate_to(f"{nginx_container}/index.html")

    # checkbox1 is unchecked by default
    assert web_client.is_checked("#checkbox1") is False
    web_client.check("#checkbox1")
    assert web_client.is_checked("#checkbox1") is True


def test_uncheck_checkbox(web_client, nginx_container: str):
    """Test unchecking a checkbox."""
    web_client.navigate_to(f"{nginx_container}/index.html")

    # checkbox2 is checked by default
    assert web_client.is_checked("#checkbox2") is True
    web_client.uncheck("#checkbox2")
    assert web_client.is_checked("#checkbox2") is False


# Element query tests


def test_get_text(web_client, nginx_container: str):
    """Test getting text content of an element."""
    web_client.navigate_to(f"{nginx_container}/index.html")

    heading_text = web_client.get_text("#main-heading")
    assert heading_text == "Welcome to Test Page"


def test_get_attribute(web_client, nginx_container: str):
    """Test getting element attribute."""
    web_client.navigate_to(f"{nginx_container}/index.html")

    placeholder = web_client.get_attribute("#username", "placeholder")
    assert placeholder == "Username"


def test_get_attribute_data_attribute(web_client, nginx_container: str):
    """Test getting data attribute."""
    web_client.navigate_to(f"{nginx_container}/index.html")

    testid = web_client.get_attribute("#text-content", "data-testid")
    assert testid == "text-box"


def test_is_visible(web_client, nginx_container: str):
    """Test checking element visibility."""
    web_client.navigate_to(f"{nginx_container}/index.html")

    assert web_client.is_visible("#main-heading") is True
    assert web_client.is_visible("#hidden-element") is False


def test_is_enabled(web_client, nginx_container: str):
    """Test checking if element is enabled."""
    web_client.navigate_to(f"{nginx_container}/index.html")

    assert web_client.is_enabled("#enabled-btn") is True
    assert web_client.is_enabled("#disabled-btn") is False


def test_get_elements_count(web_client, nginx_container: str):
    """Test counting elements matching selector."""
    web_client.navigate_to(f"{nginx_container}/index.html")

    count = web_client.get_elements_count(".paragraph")
    assert count == 3


# Page content tests


def test_contains_text(web_client, nginx_container: str):
    """Test checking if page contains text."""
    web_client.navigate_to(f"{nginx_container}/index.html")

    assert web_client.contains_text("Welcome to Test Page") is True
    assert web_client.contains_text("This text does not exist") is False


def test_get_page_source(web_client, nginx_container: str):
    """Test getting page source."""
    web_client.navigate_to(f"{nginx_container}/index.html")

    source = web_client.get_page_source()
    assert "<html>" in source or "<html" in source
    assert "Welcome to Test Page" in source
    assert "test-form" in source


# Waiting tests


def test_wait_for_element(web_client, nginx_container: str):
    """Test waiting for an element."""
    web_client.navigate_to(f"{nginx_container}/index.html")

    web_client.wait_for_element("#main-heading", timeout=5000)
    assert web_client.is_visible("#main-heading")


def test_wait_for_element_visible(web_client, nginx_container: str):
    """Test waiting for an element to be visible."""
    web_client.navigate_to(f"{nginx_container}/index.html")

    web_client.wait_for_element_visible("#main-heading", timeout=5000)
    assert web_client.is_visible("#main-heading")


# Factory tests
#
# These tests verify the factory's argument-routing logic: that the right
# client class is constructed, that the default ``client_type`` resolves to
# Playwright, and that invalid types raise the documented error.
#
# They thread the shared ``playwright_browser`` fixture in so the factory
# does not launch a second ``sync_playwright()`` context. Launching a second
# sync context in the same process interacts badly with pytest-asyncio's
# event loop (see https://github.com/microsoft/playwright-pytest/issues/35).
# The launch-on-demand path is exercised separately by any test that creates
# a ``PlayWrightWebClient`` via ``create_client()`` with no ``browser``
# argument in a fresh process.


def test_create_playwright_client(web_client_factory: WebClientFactory, playwright_browser):
    """Test creating a Playwright client with an explicit client type."""
    client = web_client_factory.create_client(
        client_type=WebClientFactory.WebClientType.PLAYWRIGHT,
        browser=playwright_browser,
    )

    assert client is not None
    assert isinstance(client, PlayWrightWebClient)
    client.close()


def test_create_client_default_type(web_client_factory: WebClientFactory, playwright_browser):
    """Test that the default ``client_type`` resolves to Playwright."""
    client = web_client_factory.create_client(browser=playwright_browser)

    assert client is not None
    assert isinstance(client, PlayWrightWebClient)
    client.close()


def test_create_client_invalid_type(web_client_factory: WebClientFactory):
    """Test creating a client with invalid type raises error."""
    with pytest.raises(ValueError, match="Unsupported client type"):
        web_client_factory.create_client(client_type="invalid")


# Context manager tests


def test_context_manager(web_client, nginx_container: str):
    """Test using web client as context manager."""
    web_client.navigate_to(f"{nginx_container}/index.html")
    assert web_client.get_title() == "Test Page"


def test_context_manager_with_exception(web_client_factory: WebClientFactory, playwright_browser):
    """Test context manager cleanup on exception.

    Verifies that ``__exit__`` runs even when an exception propagates out of
    the ``with`` block. Uses the shared browser fixture to avoid launching a
    second ``sync_playwright()`` context, which would conflict with the
    pytest-asyncio event loop.
    """
    with pytest.raises(ValueError, match="Test exception"):
        with web_client_factory.create_client(browser=playwright_browser) as client:
            assert client is not None
            raise ValueError("Test exception")


# Screenshot tests


def test_screenshot(web_client, nginx_container: str, tmp_path):
    """Test taking a screenshot."""
    web_client.navigate_to(f"{nginx_container}/index.html")

    screenshot_path = str(tmp_path / "screenshot.png")
    web_client.screenshot(screenshot_path)

    assert os.path.exists(screenshot_path)
    assert os.path.getsize(screenshot_path) > 0
