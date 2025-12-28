from klab_pytest_toolkit_web.api_client import ApiClientFactory, RestApiClient
import pytest
from testcontainers.core.container import DockerContainer
from testcontainers.core.wait_strategies import HttpWaitStrategy
from collections.abc import Generator


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


@pytest.fixture()
def rest_client(
    api_client_factory: ApiClientFactory, httpbin_container
) -> Generator[RestApiClient]:
    """Fixture to provide a REST API client."""
    with api_client_factory.create_rest_client(base_url=httpbin_container) as client:
        yield client


def test_get_request(rest_client: RestApiClient):
    """Test basic GET request with query parameters."""
    response = rest_client.get("/get", params={"test": "value"})

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["args"]["test"] == "value"


def test_get_request_with_multiple_params(rest_client: RestApiClient):
    """Test GET request with multiple query parameters."""
    response = rest_client.get(
        "/get", params={"key1": "value1", "key2": "value2", "key3": "value3"}
    )

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["args"]["key1"] == "value1"
    assert json_data["args"]["key2"] == "value2"
    assert json_data["args"]["key3"] == "value3"


def test_get_request_without_params(rest_client: RestApiClient):
    """Test GET request without query parameters."""
    response = rest_client.get("/get")

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["args"] == {}


def test_post_request(rest_client: RestApiClient):
    """Test POST request with JSON payload."""
    payload = {"name": "John Doe", "email": "john@example.com", "age": 30}

    response = rest_client.post("/post", payload=payload)

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["json"] == payload
    assert json_data["json"]["name"] == "John Doe"
    assert json_data["json"]["email"] == "john@example.com"


def test_post_request_with_nested_data(rest_client: RestApiClient):
    """Test POST request with nested JSON structure."""
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


def test_post_request_empty_payload(rest_client: RestApiClient):
    """Test POST request with empty payload."""
    response = rest_client.post("/post", payload={})

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["json"] == {}


def test_delete_request(rest_client: RestApiClient):
    """Test DELETE request."""
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


def test_session_persistence(rest_client: RestApiClient):
    """Test that session persists across requests."""
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


def test_get_with_special_characters_in_params(rest_client: RestApiClient):
    """Test GET request with special characters in parameters."""
    response = rest_client.get(
        "/get", params={"search": "test & value", "email": "user@example.com"}
    )

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["args"]["search"] == "test & value"
    assert json_data["args"]["email"] == "user@example.com"


def test_post_with_array_data(rest_client: RestApiClient):
    """Test POST request with array data."""
    payload = {"users": ["user1", "user2", "user3"], "tags": [1, 2, 3, 4, 5]}

    response = rest_client.post("/post", payload=payload)

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["json"]["users"] == ["user1", "user2", "user3"]
    assert json_data["json"]["tags"] == [1, 2, 3, 4, 5]


def test_response_content_type(rest_client: RestApiClient):
    """Test that response has correct content type."""
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


def test_put_request(rest_client: RestApiClient):
    """Test PUT request with JSON payload."""
    payload = {"id": 1, "name": "Updated Name", "email": "updated@example.com"}

    response = rest_client.put("/put", payload=payload)

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["json"] == payload
    assert json_data["json"]["name"] == "Updated Name"


def test_patch_request(rest_client: RestApiClient):
    """Test PATCH request with partial JSON payload."""
    payload = {"name": "Partially Updated"}

    response = rest_client.patch("/patch", payload=payload)

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["json"] == payload
    assert json_data["json"]["name"] == "Partially Updated"


def test_request_with_timeout(rest_client: RestApiClient):
    """Test request with custom timeout."""
    # Test with short timeout - should succeed for fast endpoint
    response = rest_client.get("/get", timeout=5)
    assert response.status_code == 200

    # Test POST with timeout
    response = rest_client.post("/post", payload={"test": "data"}, timeout=10)
    assert response.status_code == 200


def test_put_with_timeout(rest_client: RestApiClient):
    """Test PUT request with timeout."""
    response = rest_client.put("/put", payload={"id": 1}, timeout=5)

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["json"]["id"] == 1


def test_patch_with_timeout(rest_client: RestApiClient):
    """Test PATCH request with timeout."""
    response = rest_client.patch("/patch", payload={"status": "updated"}, timeout=5)

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["json"]["status"] == "updated"


def test_delete_with_timeout(rest_client: RestApiClient):
    """Test DELETE request with timeout."""
    response = rest_client.delete("/delete", timeout=5)

    assert response.status_code == 200
    json_data = response.json()
    assert "url" in json_data
