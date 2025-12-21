import pytest
from klab_pytest_toolkit_webfixtures import ResponseValidatorFactory


def test_validator_with_valid_data(
    response_validator_factory: ResponseValidatorFactory,
):
    """Test basic validation with valid data."""
    # arrange
    schema = {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"},
            "email": {"type": "string"},
        },
        "required": ["id", "name", "email"],
    }

    validator = response_validator_factory.create_json_validator(schema)
    valid_response = {"id": 1, "name": "John Doe", "email": "john@test.com"}

    # act & assert
    assert validator.validate_response(valid_response) is True
    assert validator.get_last_error() == ""


def test_validator_with_invalid_type(
    response_validator_factory: ResponseValidatorFactory,
):
    """Test validation fails when data type is incorrect."""
    # arrange
    schema = {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"},
        },
        "required": ["id", "name"],
    }

    validator = response_validator_factory.create_json_validator(schema)
    invalid_response = {
        "id": "not-a-number",  # Should be integer
        "name": "John Doe",
    }

    # act
    result = validator.validate_response(invalid_response)

    # assert
    assert result is False
    assert validator.get_last_error() is not None
    assert (
        "integer" in validator.get_last_error().lower()
        or "type" in validator.get_last_error().lower()
    )


def test_validator_with_missing_required_field(
    response_validator_factory: ResponseValidatorFactory,
):
    """Test validation fails when required field is missing."""
    # arrange
    schema = {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"},
            "email": {"type": "string"},
        },
        "required": ["id", "name", "email"],
    }

    validator = response_validator_factory.create_json_validator(schema)
    invalid_response = {
        "id": 1,
        "name": "John Doe",
        # Missing 'email' field
    }

    # act
    result = validator.validate_response(invalid_response)

    # assert
    assert result is False
    assert validator.get_last_error() is not None
    assert "email" in validator.get_last_error().lower()


def test_validator_with_extra_fields_allowed(
    response_validator_factory: ResponseValidatorFactory,
):
    """Test that additional properties are allowed by default."""
    # arrange
    schema = {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
        },
        "required": ["id"],
    }

    validator = response_validator_factory.create_json_validator(schema)
    data_with_extra = {
        "id": 1,
        "extra_field": "value",
        "another_field": 123,
    }

    # act & assert
    assert validator.validate_response(data_with_extra) is True


def test_validator_with_strict_schema(
    response_validator_factory: ResponseValidatorFactory,
):
    """Test strict schema that disallows additional properties."""
    # arrange
    schema = {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
        },
        "required": ["id"],
        "additionalProperties": False,  # Explicitly disallow extras
    }

    validator = response_validator_factory.create_json_validator(schema)
    data_with_extra = {
        "id": 1,
        "extra_field": "value",
    }

    # act & assert
    assert validator.validate_response(data_with_extra) is False
    assert "additional" in validator.get_last_error().lower()


def test_validator_with_nested_objects(
    response_validator_factory: ResponseValidatorFactory,
):
    """Test validation of nested object structures."""
    # arrange
    schema = {
        "type": "object",
        "properties": {
            "user": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                },
                "required": ["id", "name"],
            },
            "post": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["title"],
            },
        },
        "required": ["user", "post"],
    }

    validator = response_validator_factory.create_json_validator(schema)

    valid_nested = {
        "user": {"id": 1, "name": "John"},
        "post": {"title": "My Post", "content": "Content here"},
    }

    # act & assert
    assert validator.validate_response(valid_nested) is True


def test_validator_with_array_validation(
    response_validator_factory: ResponseValidatorFactory,
):
    """Test validation of array data."""
    # arrange
    schema = {
        "type": "object",
        "properties": {
            "users": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {"type": "string"},
                    },
                    "required": ["id", "name"],
                },
                "minItems": 1,
            }
        },
        "required": ["users"],
    }

    validator = response_validator_factory.create_json_validator(schema)

    valid_array_data = {
        "users": [
            {"id": 1, "name": "John"},
            {"id": 2, "name": "Jane"},
        ]
    }

    invalid_array_data = {
        "users": []  # Violates minItems: 1
    }

    # act & assert
    assert validator.validate_response(valid_array_data) is True
    assert validator.validate_response(invalid_array_data) is False


def test_validator_with_enum_constraint(
    response_validator_factory: ResponseValidatorFactory,
):
    """Test validation with enum constraints."""
    # arrange
    schema = {
        "type": "object",
        "properties": {
            "status": {"type": "string", "enum": ["pending", "active", "completed"]},
            "priority": {"type": "string", "enum": ["low", "medium", "high"]},
        },
        "required": ["status", "priority"],
    }

    validator = response_validator_factory.create_json_validator(schema)

    valid_data = {"status": "active", "priority": "high"}
    invalid_data = {"status": "invalid_status", "priority": "medium"}

    # act & assert
    assert validator.validate_response(valid_data) is True
    assert validator.validate_response(invalid_data) is False


def test_validator_with_number_constraints(
    response_validator_factory: ResponseValidatorFactory,
):
    """Test validation with numeric constraints."""
    # arrange
    schema = {
        "type": "object",
        "properties": {
            "age": {"type": "integer", "minimum": 0, "maximum": 150},
            "rating": {"type": "number", "minimum": 0.0, "maximum": 5.0},
        },
        "required": ["age", "rating"],
    }

    validator = response_validator_factory.create_json_validator(schema)

    valid_data = {"age": 25, "rating": 4.5}
    invalid_age = {"age": -5, "rating": 4.5}  # Negative age
    invalid_rating = {"age": 25, "rating": 6.0}  # Rating too high

    # act & assert
    assert validator.validate_response(valid_data) is True
    assert validator.validate_response(invalid_age) is False
    assert validator.validate_response(invalid_rating) is False


def test_validator_with_string_patterns(
    response_validator_factory: ResponseValidatorFactory,
):
    """Test validation with string pattern constraints."""
    # arrange
    schema = {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            },
            "phone": {"type": "string", "pattern": r"^\+?[1-9]\d{1,14}$"},
        },
        "required": ["email"],
    }

    validator = response_validator_factory.create_json_validator(schema)

    valid_data = {"email": "test@example.com", "phone": "+1234567890"}
    invalid_email = {"email": "not-an-email"}

    # act & assert
    assert validator.validate_response(valid_data) is True
    assert validator.validate_response(invalid_email) is False


def test_validator_with_raise_on_error(
    response_validator_factory: ResponseValidatorFactory,
):
    """Test that validator raises exception when configured to do so."""
    # arrange
    schema = {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
        },
        "required": ["id"],
    }

    validator = response_validator_factory.create_json_validator(
        schema=schema,
        raise_on_error=True,
    )

    invalid_data = {"id": "not-an-integer"}

    # act & assert
    with pytest.raises(Exception):  # Should raise ValidationError or SchemaError
        validator.validate_response(invalid_data)


def test_validator_without_raise_on_error(
    response_validator_factory: ResponseValidatorFactory,
):
    """Test that validator returns False instead of raising."""
    # arrange
    schema = {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
        },
        "required": ["id"],
    }

    validator = response_validator_factory.create_json_validator(
        schema=schema,
        raise_on_error=False,
    )

    invalid_data = {"id": "not-an-integer"}

    # act & assert
    assert validator.validate_response(invalid_data) is False


def test_multiple_validators_in_one_test(
    response_validator_factory: ResponseValidatorFactory,
):
    """Test creating multiple validators for different schemas in one test."""
    # arrange
    user_schema = {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "username": {"type": "string"},
        },
        "required": ["id", "username"],
    }

    post_schema = {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "title": {"type": "string"},
            "content": {"type": "string"},
        },
        "required": ["id", "title"],
    }

    comment_schema = {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "text": {"type": "string"},
            "author_id": {"type": "integer"},
        },
        "required": ["id", "text", "author_id"],
    }

    # act
    user_validator = response_validator_factory.create_json_validator(user_schema)
    post_validator = response_validator_factory.create_json_validator(post_schema)
    comment_validator = response_validator_factory.create_json_validator(comment_schema)

    user_data = {"id": 1, "username": "johndoe"}
    post_data = {"id": 1, "title": "My Post", "content": "Content"}
    comment_data = {"id": 1, "text": "Great post!", "author_id": 1}

    # assert
    assert user_validator.validate_response(user_data) is True
    assert post_validator.validate_response(post_data) is True
    assert comment_validator.validate_response(comment_data) is True


def test_validator_no_schema_raises_error(
    response_validator_factory: ResponseValidatorFactory,
):
    """Test that validator raises error when no schema is set."""
    # arrange
    validator = response_validator_factory.create_json_validator(schema=None)
    data = {"id": 1}

    # act & assert
    with pytest.raises(ValueError, match="No schema set for validation"):
        validator.validate_response(data)


def test_validator_with_optional_fields(
    response_validator_factory: ResponseValidatorFactory,
):
    """Test validation with optional fields."""
    # arrange
    schema = {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"},
            "description": {"type": "string"},  # Optional
        },
        "required": ["id", "name"],  # description is not required
    }

    validator = response_validator_factory.create_json_validator(schema)

    data_with_optional = {"id": 1, "name": "Test", "description": "A test"}
    data_without_optional = {"id": 1, "name": "Test"}

    # act & assert
    assert validator.validate_response(data_with_optional) is True
    assert validator.validate_response(data_without_optional) is True


def test_validator_complex_real_world_api_response(
    response_validator_factory: ResponseValidatorFactory,
):
    """Test validation of complex real-world API response structure."""
    # arrange
    schema = {
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "data": {
                "type": "object",
                "properties": {
                    "user": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "email": {"type": "string"},
                            "profile": {
                                "type": "object",
                                "properties": {
                                    "first_name": {"type": "string"},
                                    "last_name": {"type": "string"},
                                    "avatar_url": {"type": ["string", "null"]},
                                },
                            },
                        },
                        "required": ["id", "email", "profile"],
                    },
                    "posts": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer"},
                                "title": {"type": "string"},
                                "published": {"type": "boolean"},
                            },
                            "required": ["id", "title"],
                        },
                    },
                },
                "required": ["user"],
            },
            "metadata": {
                "type": "object",
                "properties": {
                    "timestamp": {"type": "string"},
                    "version": {"type": "string"},
                },
            },
        },
        "required": ["success", "data"],
    }

    validator = response_validator_factory.create_json_validator(schema)

    complex_response = {
        "success": True,
        "data": {
            "user": {
                "id": 123,
                "email": "john@example.com",
                "profile": {
                    "first_name": "John",
                    "last_name": "Doe",
                    "avatar_url": "https://example.com/avatar.jpg",
                },
            },
            "posts": [
                {"id": 1, "title": "First Post", "published": True},
                {"id": 2, "title": "Second Post", "published": False},
            ],
        },
        "metadata": {
            "timestamp": "2025-11-30T12:00:00Z",
            "version": "1.0",
        },
    }

    # act & assert
    assert validator.validate_response(complex_response) is True
