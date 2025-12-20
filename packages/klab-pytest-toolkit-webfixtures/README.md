# Klab Pytest Toolkit - Web Fixtures

Custom pytest fixtures for web testing with built-in JSON response validation.

## Installation

```bash
pip install klab-pytest-toolkit-webfixtures
```

## Features

- 🔍 **JSON Schema Validation** - Validate API responses against JSON schemas (powered by [jsonschema](https://python-jsonschema.readthedocs.io/))
- 🌐 **REST API Client** - Simple HTTP client for making API requests with session management
- Playwright integration for end-to-end web testing

## How It Works

This toolkit uses the [jsonschema](https://python-jsonschema.readthedocs.io/) library under the hood to perform JSON Schema validation. You define your expected response structure using standard JSON Schema format, and the validator checks your API responses against it. All JSON Schema features are supported, including:

- Type validation (string, integer, number, boolean, array, object, null)
- Constraints (minimum, maximum, minLength, maxLength, pattern, enum, etc.)
- Nested objects and arrays
- Required fields
- Additional properties control
- And all other [JSON Schema Draft 7](https://json-schema.org/draft-07/json-schema-release-notes.html) features

## Quick Start

### Instalation

* Playwright need some additional dependencies.

### REST API Client

```python
def test_api_call(api_client_factory):
    """Make HTTP requests to REST APIs."""
    client = api_client_factory.create_rest_client(
        base_url="https://api.example.com",
        headers={"Authorization": "Bearer token123"}
    )
    
    # GET request
    response = client.get("/users/1")
    assert response.status_code == 200
    
    # POST request
    response = client.post("/users", payload={"name": "John", "email": "john@example.com"})
    assert response.status_code == 201
    
    # DELETE request
    response = client.delete("/users/1")
    assert response.status_code == 204
```

### Combining API Client with JSON Validation

```python
def test_api_with_validation(api_client_factory, json_response_validator_factory):
    """Make API calls and validate responses."""
    # Create API client
    client = api_client_factory.create_rest_client(base_url="https://api.example.com")
    
    # Create validator
    user_schema = {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"},
            "email": {"type": "string"}
        },
        "required": ["id", "name", "email"]
    }
    validator = json_response_validator_factory.create_validator(user_schema)
    
    # Make request and validate
    response = client.get("/users/1")
    assert response.status_code == 200
    assert validator.validate_response(response.json())
```

### JSON Validator - Basic Usage

```python
def test_api_response(json_response_validator_factory):
    """Test API response validation."""
    schema = {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"},
            "email": {"type": "string"}
        },
        "required": ["id", "name", "email"]
    }
    
    validator = json_response_validator_factory.create_validator(schema)
    
    response_data = {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com"
    }
    
    assert validator.validate_response(response_data)
```

### Multiple Validators in One Test

```python
def test_multiple_endpoints(json_response_validator_factory):
    """Create multiple validators for different API endpoints."""
    user_schema = {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "username": {"type": "string"}
        },
        "required": ["id", "username"]
    }
    
    post_schema = {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "title": {"type": "string"},
            "content": {"type": "string"}
        },
        "required": ["id", "title"]
    }
    
    # Create separate validators for different schemas
    user_validator = json_response_validator_factory.create_validator(user_schema)
    post_validator = json_response_validator_factory.create_validator(post_schema)
    
    # Validate different response types
    assert user_validator.validate_response({"id": 1, "username": "john"})
    assert post_validator.validate_response({"id": 1, "title": "My Post", "content": "..."})
```

### Error Handling Options

```python
def test_with_error_handling(json_response_validator_factory):
    """Configure error handling behavior per validator."""
    schema = {
        "type": "object",
        "properties": {
            "status": {"type": "string"}
        },
        "required": ["status"]
    }
    
    # Option 1: Return False on validation error (default)
    validator_silent = json_response_validator_factory.create_validator(
        schema=schema,
        raise_on_error=False
    )
    
    # Option 2: Raise exception on validation error
    validator_strict = json_response_validator_factory.create_validator(
        schema=schema,
        raise_on_error=True
    )
    
    invalid_data = {"status": 123}  # Should be string
    
    # Silent mode returns False
    assert validator_silent.validate_response(invalid_data) is False
    print(f"Error: {validator_silent.get_last_error()}")
    
    # Strict mode raises exception
    with pytest.raises(Exception):
        validator_strict.validate_response(invalid_data)
```

### Advanced Validation Features

```python
def test_advanced_validation(json_response_validator_factory):
    """Use advanced validation features."""
    schema = {
        "type": "object",
        "properties": {
            "age": {"type": "integer", "minimum": 0, "maximum": 150},
            "email": {"type": "string", "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"},
            "status": {"type": "string", "enum": ["active", "inactive", "pending"]}
        },
        "required": ["age", "email", "status"]
    }
    
    validator = json_response_validator_factory.create_validator(schema)
    
    valid_data = {
        "age": 25,
        "email": "user@example.com",
        "status": "active"
    }
    
    assert validator.validate_response(valid_data)
```

### Strict Schema Validation

```python
def test_strict_schema(json_response_validator_factory):
    """Disallow additional properties not defined in schema."""
    schema = {
        "type": "object",
        "properties": {
            "id": {"type": "integer"}
        },
        "required": ["id"],
        "additionalProperties": False  # Reject extra fields
    }
    
    validator = json_response_validator_factory.create_validator(schema)
    
    # Valid: only defined properties
    assert validator.validate_response({"id": 1})
    
    # Invalid: has extra property
    assert validator.validate_response({"id": 1, "extra": "field"}) is False
```

### Nested and Complex Structures

```python
def test_nested_structure(json_response_validator_factory):
    """Validate complex nested JSON structures."""
    schema = {
        "type": "object",
        "properties": {
            "user": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "profile": {
                        "type": "object",
                        "properties": {
                            "first_name": {"type": "string"},
                            "last_name": {"type": "string"}
                        },
                        "required": ["first_name", "last_name"]
                    }
                },
                "required": ["id", "profile"]
            },
            "posts": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "title": {"type": "string"}
                    }
                }
            }
        },
        "required": ["user"]
    }
    
    validator = json_response_validator_factory.create_validator(schema)
    
    complex_data = {
        "user": {
            "id": 1,
            "profile": {
                "first_name": "John",
                "last_name": "Doe"
            }
        },
        "posts": [
            {"id": 1, "title": "First Post"},
            {"id": 2, "title": "Second Post"}
        ]
    }
    
    assert validator.validate_response(complex_data)
```

## Available Fixtures

### `api_client_factory`

Factory fixture that creates REST API client instances.

**Factory Method:**

```python
create_rest_client(
    base_url: str,
    headers: dict[str, str] = None
) -> RestApiClient
```

**Parameters:**
- `base_url` - Base URL for the API
- `headers` - Optional default headers for all requests

**RestApiClient Methods:**
- `get(endpoint: str, params: dict = None) -> requests.Response` - Make GET request
- `post(endpoint: str, payload: dict = None) -> requests.Response` - Make POST request
- `delete(endpoint: str) -> requests.Response` - Make DELETE request

**Example:**

```python
def test_example(api_client_factory):
    client = api_client_factory.create_rest_client(
        base_url="https://api.example.com",
        headers={"Authorization": "Bearer token"}
    )
    response = client.get("/users", params={"page": 1})
    assert response.status_code == 200
```

### `json_response_validator_factory`

Factory fixture that creates validator instances with custom configurations.

**Factory Method:**

```python
create_validator(
    schema: dict = None,
    raise_on_error: bool = False
) -> JsonResponseValidator
```

**Parameters:**
- `schema` - JSON schema dictionary for validation
- `raise_on_error` - If True, raise exceptions on validation errors; if False, return False

**Example:**

```python
def test_example(json_response_validator_factory):
    validator = json_response_validator_factory.create_validator(
        schema={"type": "object", "properties": {"id": {"type": "integer"}}},
        raise_on_error=True
    )
    assert validator.validate_response({"id": 123})
```

## Direct Class Usage

You can also use the classes directly without fixtures:

```python
from klab_pytest_toolkit_webfixtures import (
    JsonResponseValidator,
    JsonResponseValidatorFactory,
    RestApiClient,
    ApiClientFactory
)

# API Client
client = RestApiClient(
    base_url="https://api.example.com",
    headers={"Authorization": "Bearer token"}
)
response = client.get("/users/1")

# JSON Validator - Option 1: Direct instantiation
validator = JsonResponseValidator(
    schema=my_schema,
    raise_on_error=False
)

if validator.validate_response(data):
    print("Valid!")
else:
    print(f"Error: {validator.get_last_error()}")

# JSON Validator - Option 2: Using the factory
factory = JsonResponseValidatorFactory()
validator = factory.create_validator(schema=my_schema)
```

## API Reference

### ApiClientFactory

**Methods:**

- `create_rest_client(base_url: str, headers: dict = None) -> RestApiClient`
  - Create a new REST API client instance

### RestApiClient

**Methods:**

- `get(endpoint: str, params: dict = None) -> requests.Response`
  - Make a GET request
  
- `post(endpoint: str, payload: dict = None) -> requests.Response`
  - Make a POST request with JSON payload
  
- `delete(endpoint: str) -> requests.Response`
  - Make a DELETE request

**Constructor Parameters:**

- `base_url` - Base URL for the API
- `headers` (optional) - Default headers for all requests

### JsonResponseValidatorFactory

**Methods:**

- `create_validator(schema: dict = None, raise_on_error: bool = False) -> JsonResponseValidator`
  - Create a new validator instance with specified configuration

### JsonResponseValidator

**Methods:**

- `validate_response(response_data: dict) -> bool`
  - Validate response data against schema
  - Returns True if valid, False if invalid (unless raise_on_error=True)

- `get_last_error() -> str | None`
  - Get the last validation error message
  - Returns None if last validation was successful

**Constructor Parameters:**

- `schema` (optional) - JSON schema dictionary
- `raise_on_error` (default: False) - Raise exceptions on validation failure

## Real-World Examples

### Testing REST API with testcontainers

```python
import pytest
from testcontainers.core.container import DockerContainer
from testcontainers.core.wait_strategies import HttpWaitStrategy

@pytest.fixture(scope="session")
def httpbin_container():
    """Start an HTTPBin container for testing."""
    with DockerContainer("kennethreitz/httpbin:latest") as httpbin:
        httpbin.with_exposed_ports(80)
        httpbin.waiting_for(HttpWaitStrategy(path="/get", port=80).for_status_code(200))
        httpbin.start()
        port = httpbin.get_exposed_port(80)
        yield f"http://localhost:{port}"

def test_get_request(api_client_factory, httpbin_container):
    """Test GET request with query parameters."""
    client = api_client_factory.create_rest_client(base_url=httpbin_container)
    
    response = client.get("/get", params={"test": "value"})
    
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["args"]["test"] == "value"
```

### Complete Integration Test

```python
def test_user_api_endpoint(api_client_factory, json_response_validator_factory):
    """Test user API endpoint response structure with validation."""
    # Setup API client
    client = api_client_factory.create_rest_client(
        base_url="https://api.example.com",
        headers={"Authorization": "Bearer token"}
    )
    
    # Setup validator
    schema = {
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "data": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "email": {"type": "string"},
                    "created_at": {"type": "string"}
                },
                "required": ["id", "email"]
            }
        },
        "required": ["success", "data"]
    }
    validator = json_response_validator_factory.create_validator(schema)
    
    # Make request
    response = client.get("/users/123")
    assert response.status_code == 200
    
    # Validate response
    assert validator.validate_response(response.json())
```

### Testing Multiple API Versions

```python
def test_api_version_compatibility(json_response_validator_factory):
    """Test different API versions have correct response structures."""
    v1_schema = {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"}
        }
    }
    
    v2_schema = {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "first_name": {"type": "string"},
            "last_name": {"type": "string"}
        }
    }
    
    v1_validator = json_response_validator_factory.create_validator(v1_schema)
    v2_validator = json_response_validator_factory.create_validator(v2_schema)
    
    v1_response = {"id": 1, "name": "John Doe"}
    v2_response = {"id": 1, "first_name": "John", "last_name": "Doe"}
    
    assert v1_validator.validate_response(v1_response)
    assert v2_validator.validate_response(v2_response)
```

## Common Patterns

### Pattern: Reusable Schema Definitions

```python
# conftest.py
@pytest.fixture
def user_schema():
    return {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "username": {"type": "string"}
        },
        "required": ["id", "username"]
    }

# test_api.py
def test_get_user(json_response_validator_factory, user_schema):
    validator = json_response_validator_factory.create_validator(user_schema)
    response = api_client.get_user(1)
    assert validator.validate_response(response)
```

### Pattern: Validation Helper

```python
# conftest.py
@pytest.fixture
def validate_json(json_response_validator_factory):
    """Helper fixture for quick validation."""
    def _validate(data, schema):
        validator = json_response_validator_factory.create_validator(schema)
        return validator.validate_response(data)
    return _validate

# test_api.py
def test_quick_validation(validate_json):
    schema = {"type": "object", "properties": {"id": {"type": "integer"}}}
    assert validate_json({"id": 1}, schema)
```

## Examples

See the test files for comprehensive examples:
- `tests/test_jsonvalidator.py` - JSON validation examples covering basic validation, type checking, nested objects, constraints, and error handling
- `tests/test_restapiclient.py` - REST API client examples with testcontainers integration

## License

MIT
