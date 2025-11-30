from klab_pytest_toolkit_webfixtures.api_client import ApiClientFactory
import pytest
from testcontainers.core.container import DockerContainer
from testcontainers.core.wait_strategies import HttpWaitStrategy


@pytest.fixture(scope="session")
def httpbin_container():
    """Fixture to provide an HTTPBin container for testing."""

    with DockerContainer("kennethreitz/httpbin:latest") as httpbin:
        httpbin.with_exposed_ports(80)
        httpbin.waiting_for(HttpWaitStrategy(path="/get", port=80).for_status_code(200))
        httpbin.start()
        port = httpbin.get_exposed_port(80)
        base_url = f"http://localhost:{port}"
        yield base_url


def test_get_request(api_client_factory: ApiClientFactory, httpbin_container):
    """Test basic GET request with query parameters."""
    rest_client = api_client_factory.create_rest_client(base_url=httpbin_container)

    response = rest_client.get("/get", params={"test": "value"})

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["args"]["test"] == "value"


def test_get_request_with_multiple_params(api_client_factory: ApiClientFactory, httpbin_container):
    """Test GET request with multiple query parameters."""
    rest_client = api_client_factory.create_rest_client(base_url=httpbin_container)

    response = rest_client.get(
        "/get", params={"key1": "value1", "key2": "value2", "key3": "value3"}
    )

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["args"]["key1"] == "value1"
    assert json_data["args"]["key2"] == "value2"
    assert json_data["args"]["key3"] == "value3"


def test_get_request_without_params(api_client_factory: ApiClientFactory, httpbin_container):
    """Test GET request without query parameters."""
    rest_client = api_client_factory.create_rest_client(base_url=httpbin_container)

    response = rest_client.get("/get")

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["args"] == {}


def test_post_request(api_client_factory: ApiClientFactory, httpbin_container):
    """Test POST request with JSON payload."""
    rest_client = api_client_factory.create_rest_client(base_url=httpbin_container)

    payload = {"name": "John Doe", "email": "john@example.com", "age": 30}

    response = rest_client.post("/post", payload=payload)

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["json"] == payload
    assert json_data["json"]["name"] == "John Doe"
    assert json_data["json"]["email"] == "john@example.com"


def test_post_request_with_nested_data(api_client_factory: ApiClientFactory, httpbin_container):
    """Test POST request with nested JSON structure."""
    rest_client = api_client_factory.create_rest_client(base_url=httpbin_container)

    payload = {
        "user": {"id": 1, "name": "John Doe", "profile": {"age": 30, "city": "NYC"}},
        "posts": [
            {"id": 1, "title": "First Post"},
            {"id": 2, "title": "Second Post"},
        ],
    }

    response = rest_client.post("/post", payload=payload)

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["json"] == payload
    assert json_data["json"]["user"]["name"] == "John Doe"
    assert len(json_data["json"]["posts"]) == 2


def test_post_request_empty_payload(api_client_factory: ApiClientFactory, httpbin_container):
    """Test POST request with empty payload."""
    rest_client = api_client_factory.create_rest_client(base_url=httpbin_container)

    response = rest_client.post("/post", payload={})

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["json"] == {}


def test_delete_request(api_client_factory: ApiClientFactory, httpbin_container):
    """Test DELETE request."""
    rest_client = api_client_factory.create_rest_client(base_url=httpbin_container)

    response = rest_client.delete("/delete")

    assert response.status_code == 200
    json_data = response.json()
    assert "url" in json_data
    assert json_data["url"].endswith("/delete")


def test_client_with_custom_headers(api_client_factory: ApiClientFactory, httpbin_container):
    """Test client with custom headers."""
    custom_headers = {
        "Authorization": "Bearer test-token",
        "X-Custom-Header": "custom-value",
    }

    rest_client = api_client_factory.create_rest_client(
        base_url=httpbin_container, headers=custom_headers
    )

    response = rest_client.get("/headers")

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["headers"]["Authorization"] == "Bearer test-token"
    assert json_data["headers"]["X-Custom-Header"] == "custom-value"


def test_client_base_url_handling(api_client_factory: ApiClientFactory, httpbin_container):
    """Test that base URL is properly combined with endpoint."""
    rest_client = api_client_factory.create_rest_client(base_url=httpbin_container)

    response = rest_client.get("/get")

    assert response.status_code == 200
    json_data = response.json()
    assert httpbin_container in json_data["url"]


def test_session_persistence(api_client_factory: ApiClientFactory, httpbin_container):
    """Test that session persists across requests."""
    rest_client = api_client_factory.create_rest_client(base_url=httpbin_container)

    # First request sets a cookie
    response1 = rest_client.get("/cookies/set?session=test123")
    assert response1.status_code == 200

    # Second request should have the cookie
    response2 = rest_client.get("/cookies")
    json_data = response2.json()
    assert json_data["cookies"]["session"] == "test123"


def test_multiple_clients_independent(api_client_factory: ApiClientFactory, httpbin_container):
    """Test that multiple clients are independent."""
    client1 = api_client_factory.create_rest_client(
        base_url=httpbin_container, headers={"X-Client": "client1"}
    )

    client2 = api_client_factory.create_rest_client(
        base_url=httpbin_container, headers={"X-Client": "client2"}
    )

    response1 = client1.get("/headers")
    response2 = client2.get("/headers")

    assert response1.json()["headers"]["X-Client"] == "client1"
    assert response2.json()["headers"]["X-Client"] == "client2"


def test_get_with_special_characters_in_params(
    api_client_factory: ApiClientFactory, httpbin_container
):
    """Test GET request with special characters in parameters."""
    rest_client = api_client_factory.create_rest_client(base_url=httpbin_container)

    response = rest_client.get(
        "/get", params={"search": "test & value", "email": "user@example.com"}
    )

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["args"]["search"] == "test & value"
    assert json_data["args"]["email"] == "user@example.com"


def test_post_with_array_data(api_client_factory: ApiClientFactory, httpbin_container):
    """Test POST request with array data."""
    rest_client = api_client_factory.create_rest_client(base_url=httpbin_container)

    payload = {"users": ["user1", "user2", "user3"], "tags": [1, 2, 3, 4, 5]}

    response = rest_client.post("/post", payload=payload)

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["json"]["users"] == ["user1", "user2", "user3"]
    assert json_data["json"]["tags"] == [1, 2, 3, 4, 5]


def test_response_content_type(api_client_factory: ApiClientFactory, httpbin_container):
    """Test that response has correct content type."""
    rest_client = api_client_factory.create_rest_client(base_url=httpbin_container)

    response = rest_client.get("/get")

    assert response.status_code == 200
    assert "application/json" in response.headers["Content-Type"]


def test_factory_creates_new_instances(api_client_factory: ApiClientFactory):
    """Test that factory creates independent client instances."""
    client1 = api_client_factory.create_rest_client(base_url="http://api1.example.com")
    client2 = api_client_factory.create_rest_client(base_url="http://api2.example.com")

    assert client1.base_url != client2.base_url
    assert client1.session is not client2.session
    assert id(client1) != id(client2)


def test_put_request(api_client_factory: ApiClientFactory, httpbin_container):
    """Test PUT request with JSON payload."""
    rest_client = api_client_factory.create_rest_client(base_url=httpbin_container)

    payload = {"id": 1, "name": "Updated Name", "email": "updated@example.com"}

    response = rest_client.put("/put", payload=payload)

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["json"] == payload
    assert json_data["json"]["name"] == "Updated Name"


def test_patch_request(api_client_factory: ApiClientFactory, httpbin_container):
    """Test PATCH request with partial JSON payload."""
    rest_client = api_client_factory.create_rest_client(base_url=httpbin_container)

    payload = {"name": "Partially Updated"}

    response = rest_client.patch("/patch", payload=payload)

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["json"] == payload
    assert json_data["json"]["name"] == "Partially Updated"


def test_request_with_timeout(api_client_factory: ApiClientFactory, httpbin_container):
    """Test request with custom timeout."""
    rest_client = api_client_factory.create_rest_client(base_url=httpbin_container)

    # Test with short timeout - should succeed for fast endpoint
    response = rest_client.get("/get", timeout=5)
    assert response.status_code == 200

    # Test POST with timeout
    response = rest_client.post("/post", payload={"test": "data"}, timeout=10)
    assert response.status_code == 200


def test_put_with_timeout(api_client_factory: ApiClientFactory, httpbin_container):
    """Test PUT request with timeout."""
    rest_client = api_client_factory.create_rest_client(base_url=httpbin_container)

    response = rest_client.put("/put", payload={"id": 1}, timeout=5)

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["json"]["id"] == 1


def test_patch_with_timeout(api_client_factory: ApiClientFactory, httpbin_container):
    """Test PATCH request with timeout."""
    rest_client = api_client_factory.create_rest_client(base_url=httpbin_container)

    response = rest_client.patch("/patch", payload={"status": "updated"}, timeout=5)

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["json"]["status"] == "updated"


def test_delete_with_timeout(api_client_factory: ApiClientFactory, httpbin_container):
    """Test DELETE request with timeout."""
    rest_client = api_client_factory.create_rest_client(base_url=httpbin_container)

    response = rest_client.delete("/delete", timeout=5)

    assert response.status_code == 200
    json_data = response.json()
    assert "url" in json_data
