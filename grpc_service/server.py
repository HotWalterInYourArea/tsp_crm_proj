from concurrent import futures
import grpc
import logging

from grpc_service.proto import commission_pb2_grpc
from grpc_service.servicer import CommissionServicer

logging.basicConfig(level=logging.INFO)


def serve(port: int = 50051):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    commission_pb2_grpc.add_CommissionServiceServicer_to_server(
        CommissionServicer(), server,
    )
    server.add_insecure_port(f"0.0.0.0:{port}")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()