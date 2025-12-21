"""Tests for WebClient using testcontainers with nginx."""

import os

import pytest
from testcontainers.core.container import DockerContainer

from klab_pytest_toolkit_webfixtures import WebClientFactory


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


def test_navigate_to(web_client_factory: WebClientFactory, nginx_container: str):
    """Test navigating to a URL."""
    with web_client_factory.create_client(headless=True) as client:
        client.navigate_to(f"{nginx_container}/index.html")

        assert "Test Page" in client.get_title()


def test_get_url(web_client_factory: WebClientFactory, nginx_container: str):
    """Test getting current URL."""
    with web_client_factory.create_client(headless=True) as client:
        client.navigate_to(f"{nginx_container}/index.html")

        assert nginx_container in client.get_url()
        assert "index.html" in client.get_url()


def test_get_title(web_client_factory: WebClientFactory, nginx_container: str):
    """Test getting page title."""
    with web_client_factory.create_client(headless=True) as client:
        client.navigate_to(f"{nginx_container}/index.html")

        assert client.get_title() == "Test Page"


# Element interaction tests


def test_click(web_client_factory: WebClientFactory, nginx_container: str):
    """Test clicking on an element."""
    with web_client_factory.create_client(headless=True) as client:
        client.navigate_to(f"{nginx_container}/index.html")
        client.click("#about-link")

        assert "about.html" in client.get_url()
        assert "About Page" in client.get_title()


def test_fill(web_client_factory: WebClientFactory, nginx_container: str):
    """Test filling a form field."""
    with web_client_factory.create_client(headless=True) as client:
        client.navigate_to(f"{nginx_container}/index.html")

        client.fill("#username", "testuser")
        client.fill("#password", "testpass")
        client.fill("#email", "test@example.com")

        assert client.get_input_value("#username") == "testuser"
        assert client.get_input_value("#password") == "testpass"
        assert client.get_input_value("#email") == "test@example.com"


def test_select_option(web_client_factory: WebClientFactory, nginx_container: str):
    """Test selecting an option from a dropdown."""
    with web_client_factory.create_client(headless=True) as client:
        client.navigate_to(f"{nginx_container}/index.html")

        client.select_option("#dropdown", "option2")

        selected_value = client.get_input_value("#dropdown")
        assert selected_value == "option2"


def test_check_checkbox(web_client_factory: WebClientFactory, nginx_container: str):
    """Test checking a checkbox."""
    with web_client_factory.create_client(headless=True) as client:
        client.navigate_to(f"{nginx_container}/index.html")

        # checkbox1 is unchecked by default
        assert client.is_checked("#checkbox1") is False
        client.check("#checkbox1")
        assert client.is_checked("#checkbox1") is True


def test_uncheck_checkbox(web_client_factory: WebClientFactory, nginx_container: str):
    """Test unchecking a checkbox."""
    with web_client_factory.create_client(headless=True) as client:
        client.navigate_to(f"{nginx_container}/index.html")

        # checkbox2 is checked by default
        assert client.is_checked("#checkbox2") is True
        client.uncheck("#checkbox2")
        assert client.is_checked("#checkbox2") is False


# Element query tests


def test_get_text(web_client_factory: WebClientFactory, nginx_container: str):
    """Test getting text content of an element."""
    with web_client_factory.create_client(headless=True) as client:
        client.navigate_to(f"{nginx_container}/index.html")

        heading_text = client.get_text("#main-heading")

        assert heading_text == "Welcome to Test Page"


def test_get_attribute(web_client_factory: WebClientFactory, nginx_container: str):
    """Test getting element attribute."""
    with web_client_factory.create_client(headless=True) as client:
        client.navigate_to(f"{nginx_container}/index.html")

        placeholder = client.get_attribute("#username", "placeholder")

        assert placeholder == "Username"


def test_get_attribute_data_attribute(web_client_factory: WebClientFactory, nginx_container: str):
    """Test getting data attribute."""
    with web_client_factory.create_client(headless=True) as client:
        client.navigate_to(f"{nginx_container}/index.html")

        testid = client.get_attribute("#text-content", "data-testid")

        assert testid == "text-box"


def test_is_visible(web_client_factory: WebClientFactory, nginx_container: str):
    """Test checking element visibility."""
    with web_client_factory.create_client(headless=True) as client:
        client.navigate_to(f"{nginx_container}/index.html")

        assert client.is_visible("#main-heading") is True
        assert client.is_visible("#hidden-element") is False


def test_is_enabled(web_client_factory: WebClientFactory, nginx_container: str):
    """Test checking if element is enabled."""
    with web_client_factory.create_client(headless=True) as client:
        client.navigate_to(f"{nginx_container}/index.html")

        assert client.is_enabled("#enabled-btn") is True
        assert client.is_enabled("#disabled-btn") is False


def test_get_elements_count(web_client_factory: WebClientFactory, nginx_container: str):
    """Test counting elements matching selector."""
    with web_client_factory.create_client(headless=True) as client:
        client.navigate_to(f"{nginx_container}/index.html")

        count = client.get_elements_count(".paragraph")

        assert count == 3


# Page content tests


def test_contains_text(web_client_factory: WebClientFactory, nginx_container: str):
    """Test checking if page contains text."""
    with web_client_factory.create_client(headless=True) as client:
        client.navigate_to(f"{nginx_container}/index.html")

        assert client.contains_text("Welcome to Test Page") is True
        assert client.contains_text("This text does not exist") is False


def test_get_page_source(web_client_factory: WebClientFactory, nginx_container: str):
    """Test getting page source."""
    with web_client_factory.create_client(headless=True) as client:
        client.navigate_to(f"{nginx_container}/index.html")

        source = client.get_page_source()

        assert "<html>" in source or "<html" in source
        assert "Welcome to Test Page" in source
        assert "test-form" in source


# Waiting tests


def test_wait_for_element(web_client_factory: WebClientFactory, nginx_container: str):
    """Test waiting for an element."""
    with web_client_factory.create_client(headless=True) as client:
        client.navigate_to(f"{nginx_container}/index.html")

        client.wait_for_element("#main-heading", timeout=5000)

        assert client.is_visible("#main-heading")


def test_wait_for_element_visible(web_client_factory: WebClientFactory, nginx_container: str):
    """Test waiting for an element to be visible."""
    with web_client_factory.create_client(headless=True) as client:
        client.navigate_to(f"{nginx_container}/index.html")

        client.wait_for_element_visible("#main-heading", timeout=5000)

        assert client.is_visible("#main-heading")


# Factory tests


def test_create_playwright_client(web_client_factory: WebClientFactory):
    """Test creating a Playwright client."""
    client = web_client_factory.create_client(client_type=WebClientFactory.WebClientType.PLAYWRIGHT)

    assert client is not None
    client.close()


def test_create_client_default_type(web_client_factory: WebClientFactory):
    """Test creating a client with default type."""
    client = web_client_factory.create_client()

    assert client is not None
    client.close()


def test_create_client_invalid_type(web_client_factory: WebClientFactory):
    """Test creating a client with invalid type raises error."""
    with pytest.raises(ValueError, match="Unsupported client type"):
        web_client_factory.create_client(client_type="invalid")


# Context manager tests


def test_context_manager(web_client_factory: WebClientFactory, nginx_container: str):
    """Test using web client as context manager."""
    with web_client_factory.create_client(headless=True) as client:
        client.navigate_to(f"{nginx_container}/index.html")
        assert client.get_title() == "Test Page"


def test_context_manager_with_exception(web_client_factory: WebClientFactory, nginx_container: str):
    """Test context manager cleanup on exception."""
    try:
        with web_client_factory.create_client(headless=True) as client:
            client.navigate_to(f"{nginx_container}/index.html")
            raise ValueError("Test exception")
    except ValueError:
        pass


# Screenshot tests


def test_screenshot(web_client_factory: WebClientFactory, nginx_container: str, tmp_path):
    """Test taking a screenshot."""
    with web_client_factory.create_client(headless=True) as client:
        client.navigate_to(f"{nginx_container}/index.html")

        screenshot_path = str(tmp_path / "screenshot.png")
        client.screenshot(screenshot_path)

        assert os.path.exists(screenshot_path)
        assert os.path.getsize(screenshot_path) > 0
