FROM python:3.11-slim

WORKDIR /app

# Install grpc dependencies
RUN pip install --no-cache-dir grpcio==1.66.0 grpcio-tools==1.66.0 grpcio-reflection==1.66.0

# Copy proto file and server code
COPY helloworld.proto .
COPY server.py .

# Generate proto files
RUN python -m grpc_tools.protoc \
    --proto_path=. \
    --python_out=. \
    --grpc_python_out=. \
    helloworld.proto

# Expose gRPC port
EXPOSE 50051

# Run the server
CMD ["python", "server.py"]
