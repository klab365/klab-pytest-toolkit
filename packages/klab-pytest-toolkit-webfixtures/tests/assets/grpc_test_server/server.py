"""Simple gRPC server for testing."""

import grpc
from concurrent import futures
import time

# Import generated proto files
import helloworld_pb2
import helloworld_pb2_grpc


class GreeterServicer(helloworld_pb2_grpc.GreeterServicer):
    """Implementation of the Greeter service."""

    def SayHello(self, request, context):
        """Say hello to the given name."""
        return helloworld_pb2.HelloReply(message=f"Hello {request.name}")

    def SayHelloAgain(self, request, context):
        """Say hello again to the given name."""
        return helloworld_pb2.HelloReply(message=f"Hello again {request.name}")

    def SayHelloStream(self, request, context):
        """Stream hello messages to the given name."""
        for i in range(5):
            yield helloworld_pb2.HelloReply(message=f"Hello {request.name} #{i+1}")
            time.sleep(0.1)  # Small delay to simulate streaming


def serve():
    """Start the gRPC server."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    helloworld_pb2_grpc.add_GreeterServicer_to_server(GreeterServicer(), server)

    # Enable reflection for service discovery
    from grpc_reflection.v1alpha import reflection

    SERVICE_NAMES = (
        "helloworld.Greeter",
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)

    server.add_insecure_port("[::]:50051")
    server.start()
    print("gRPC server started on port 50051", flush=True)

    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == "__main__":
    serve()
