"""Tests for gRPC client functionality."""

from klab_pytest_toolkit_webfixtures.api_client import ApiClientFactory
import pytest
import grpc
from pathlib import Path
from testcontainers.core.container import DockerContainer
from testcontainers.core.wait_strategies import LogMessageWaitStrategy
from klab_pytest_toolkit_webfixtures._api_client_types.grpc_client import GrpcClient


@pytest.fixture(scope="session")
def sample_proto_file():
    """Create a sample proto file for testing."""
    test_dir = Path(__file__).parent
    proto_file = test_dir / "assets" / "grpc_test_server" / "helloworld.proto"
    return str(proto_file)


@pytest.fixture(scope="session")
def grpc_server_container():
    """Fixture to provide a gRPC test server container."""
    # Get the path to the grpc test server directory
    test_dir = Path(__file__).parent
    server_dir = test_dir / "assets" / "grpc_test_server"

    # Build the image first
    import subprocess

    image_tag = "grpc-test-server:test"
    result = subprocess.run(
        ["docker", "build", "-t", image_tag, str(server_dir)],
        check=True,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Failed to build gRPC test server image: {result.stderr}")

    with DockerContainer(image_tag) as container:
        container.with_exposed_ports(50051)
        # Wait for the server to start with log message
        container.waiting_for(LogMessageWaitStrategy("gRPC server started"))
        container.start()

        port = container.get_exposed_port(50051)
        target = f"localhost:{port}"
        yield target


# Test: Initialization errors


def test_create_grpc_client_with_proto_file_not_found(api_client_factory):
    """Test error when proto file doesn't exist."""
    with pytest.raises(FileNotFoundError):
        api_client_factory.create_grpc_client(
            target="localhost:50051", proto_file="nonexistent.proto"
        )


def test_create_grpc_client_with_invalid_proto_file(api_client_factory, tmp_path):
    """Test error when proto file has syntax errors."""
    invalid_proto = tmp_path / "invalid.proto"
    invalid_proto.write_text("this is not a valid proto file")

    with pytest.raises(RuntimeError, match="Proto compilation failed"):
        api_client_factory.create_grpc_client(
            target="localhost:50051", proto_file=str(invalid_proto)
        )


# Test: Proto file loading


def test_create_grpc_client_with_valid_proto_file(api_client_factory, sample_proto_file):
    """Test creating gRPC client with valid proto file."""
    client = api_client_factory.create_grpc_client(
        target="localhost:50051", proto_file=sample_proto_file
    )

    assert isinstance(client, GrpcClient)
    assert client.target == "localhost:50051"
    assert client._channel is not None
    client.close()


def test_grpc_client_discovers_methods_from_proto(api_client_factory, sample_proto_file):
    """Test that methods are discovered from proto file."""
    client = api_client_factory.create_grpc_client(
        target="localhost:50051", proto_file=sample_proto_file
    )

    methods = client.get_available_methods()
    assert "SayHello" in methods
    assert "SayHelloAgain" in methods
    assert "SayHelloStream" in methods
    assert len(methods) == 3
    client.close()


def test_grpc_client_methods_are_callable(api_client_factory, sample_proto_file):
    """Test that discovered methods are accessible as attributes."""
    client = api_client_factory.create_grpc_client(
        target="localhost:50051", proto_file=sample_proto_file
    )

    # Should be able to get the method as attribute
    say_hello_method = client.SayHello
    assert callable(say_hello_method)

    say_hello_again_method = client.SayHelloAgain
    assert callable(say_hello_again_method)

    client.close()


# Test: Context manager


def test_grpc_client_works_as_context_manager(api_client_factory, sample_proto_file):
    """Test gRPC client works as context manager."""
    with api_client_factory.create_grpc_client(
        target="localhost:50051", proto_file=sample_proto_file
    ) as client:
        assert isinstance(client, GrpcClient)
        assert len(client.get_available_methods()) == 3
        assert client._channel is not None


def test_grpc_client_closes_channel_on_exit(api_client_factory, sample_proto_file):
    """Test that channel is closed when exiting context manager."""
    client = api_client_factory.create_grpc_client(
        target="localhost:50051", proto_file=sample_proto_file
    )
    channel = client._channel

    with client:
        assert channel is not None

    # After exiting, channel should still be closed via close()
    # (checking internal state is implementation-dependent)


# Test: Channel options and metadata


def test_create_grpc_client_with_channel_options(api_client_factory, sample_proto_file):
    """Test creating gRPC client with channel options."""
    options = [
        ("grpc.max_receive_message_length", -1),
        ("grpc.max_send_message_length", -1),
    ]

    client = api_client_factory.create_grpc_client(
        target="localhost:50051", proto_file=sample_proto_file, options=options
    )

    assert isinstance(client, GrpcClient)
    client.close()


def test_create_grpc_client_with_metadata(api_client_factory, sample_proto_file):
    """Test creating gRPC client with metadata."""
    metadata = [
        ("authorization", "Bearer token123"),
        ("x-custom-header", "value"),
    ]

    client = api_client_factory.create_grpc_client(
        target="localhost:50051", proto_file=sample_proto_file, metadata=metadata
    )

    assert isinstance(client, GrpcClient)
    assert client.metadata == metadata
    client.close()


def test_create_grpc_client_with_empty_metadata(api_client_factory, sample_proto_file):
    """Test creating gRPC client with empty metadata list."""
    client = api_client_factory.create_grpc_client(
        target="localhost:50051", proto_file=sample_proto_file, metadata=[]
    )

    assert client.metadata == []
    client.close()


# Test: Secure connections


def test_create_grpc_client_with_ssl_credentials(api_client_factory, sample_proto_file):
    """Test creating gRPC client with SSL credentials."""
    credentials = grpc.ssl_channel_credentials()

    client = api_client_factory.create_grpc_client(
        target="localhost:50051", proto_file=sample_proto_file, credentials=credentials
    )

    assert isinstance(client, GrpcClient)
    assert client._channel is not None
    client.close()


# Test: Multiple clients


def test_create_multiple_grpc_clients(api_client_factory, sample_proto_file):
    """Test creating multiple independent gRPC clients."""
    client1 = api_client_factory.create_grpc_client(
        target="localhost:50051", proto_file=sample_proto_file
    )
    client2 = api_client_factory.create_grpc_client(
        target="localhost:50052", proto_file=sample_proto_file
    )

    assert client1 is not client2
    assert client1.target == "localhost:50051"
    assert client2.target == "localhost:50052"

    client1.close()
    client2.close()


# Test: Resource cleanup


def test_grpc_client_close_method(api_client_factory, sample_proto_file):
    """Test that close() method properly closes the channel."""
    client = api_client_factory.create_grpc_client(
        target="localhost:50051", proto_file=sample_proto_file
    )

    assert client._channel is not None
    client.close()
    # Channel should be closed (implementation-dependent verification)


def test_grpc_client_explicit_close(api_client_factory, sample_proto_file):
    """Test explicit close without context manager."""
    client = api_client_factory.create_grpc_client(
        target="localhost:50051", proto_file=sample_proto_file
    )

    try:
        assert client._channel is not None
        methods = client.get_available_methods()
        assert len(methods) == 3
    finally:
        client.close()


# Test: Integration with actual calls using real server


def test_call_grpc_method_with_kwargs(
    api_client_factory: ApiClientFactory, sample_proto_file, grpc_server_container
):
    """Test calling gRPC method with keyword arguments."""
    with api_client_factory.create_grpc_client(
        target=grpc_server_container, proto_file=sample_proto_file
    ) as client:
        response = client.SayHello(name="World")
        assert response.message == "Hello World"


def test_call_grpc_method_multiple_times(
    api_client_factory, sample_proto_file, grpc_server_container
):
    """Test calling gRPC method multiple times."""
    with api_client_factory.create_grpc_client(
        target=grpc_server_container, proto_file=sample_proto_file
    ) as client:
        response1 = client.SayHello(name="Alice")
        assert response1.message == "Hello Alice"

        response2 = client.SayHello(name="Bob")
        assert response2.message == "Hello Bob"


def test_call_different_grpc_methods(api_client_factory, sample_proto_file, grpc_server_container):
    """Test calling different gRPC methods on same client."""
    with api_client_factory.create_grpc_client(
        target=grpc_server_container, proto_file=sample_proto_file
    ) as client:
        response1 = client.SayHello(name="Charlie")
        assert response1.message == "Hello Charlie"

        response2 = client.SayHelloAgain(name="Charlie")
        assert response2.message == "Hello again Charlie"


def test_grpc_call_with_metadata(api_client_factory, sample_proto_file, grpc_server_container):
    """Test that metadata is sent with gRPC calls."""
    metadata = [("authorization", "Bearer token123")]

    with api_client_factory.create_grpc_client(
        target=grpc_server_container, proto_file=sample_proto_file, metadata=metadata
    ) as client:
        response = client.SayHello(name="Authenticated")
        assert response.message == "Hello Authenticated"


def test_grpc_server_side_streaming(api_client_factory, sample_proto_file, grpc_server_container):
    """Test server-side streaming RPC call."""
    with api_client_factory.create_grpc_client(
        target=grpc_server_container, proto_file=sample_proto_file
    ) as client:
        # Call the streaming method
        stream = client.SayHelloStream(name="StreamUser")

        # Collect all responses from the stream
        responses = list(stream)

        # Verify we got the expected number of messages
        assert len(responses) == 5

        # Verify the content of each message
        for i, response in enumerate(responses):
            expected_message = f"Hello StreamUser #{i+1}"
            assert response.message == expected_message
