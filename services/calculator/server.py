"""
Calculator Server

Starts an RPC server that hosts the Calculator service.
Parses the IDL, generates code, and handles client requests.
"""

import sys
import os
import time
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from rpc_framework.idl.parser import IDLParser
from rpc_framework.idl.generator import CodeGenerator
from rpc_framework.transport.tcp_server import TCPServer
from rpc_framework.runtime.skeleton import RPCSkeleton
from rpc_framework.runtime.registry import ServiceRegistry
from rpc_framework.utils import setup_logger
from services.calculator.calculator_impl import Calculator

logger = setup_logger(__name__, "INFO")


def main():
    """Start the Calculator RPC server."""
    print("\n" + "="*60)
    print("Calculator RPC Server")
    print("="*60 + "\n")

    # Parse IDL
    print("[1/4] Parsing Calculator.idl...")
    idl_file = os.path.join(os.path.dirname(__file__), "calculator.idl")
    parser = IDLParser()
    services = parser.parse_file(idl_file)
    print(f"✓ Parsed {len(services)} service(s)")

    # Generate code (for reference)
    print("\n[2/4] Generating RPC code...")
    generator = CodeGenerator(parser)
    generated_files = generator.generate_all()
    print(f"✓ Generated {len(generated_files)} file(s)")

    # Create service implementation and registry
    print("\n[3/4] Registering service...")
    calc = Calculator()
    registry = ServiceRegistry()

    # Register methods
    methods = {
        "add": calc.add,
        "subtract": calc.subtract,
        "multiply": calc.multiply,
        "divide": calc.divide,
        "greet": calc.greet,
    }

    # Register parameter signatures for type validation
    signatures = {
        "add": [int, int],
        "subtract": [int, int],
        "multiply": [int, int],
        "divide": [int, int],
        "greet": [str],
    }

    registry.register_service("Calculator", calc, methods, signatures)
    skeleton = RPCSkeleton(registry)
    print("✓ Service registered")

    # Start server
    print("\n[4/4] Starting TCP server...")
    server = TCPServer(host="127.0.0.1", port=5000, max_connections=10)
    server.start(request_handler=skeleton.dispatch_request)
    print("✓ Server started on 127.0.0.1:5000")

    print("\n" + "="*60)
    print("Server is running. Press Ctrl+C to stop.")
    print("="*60 + "\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nShutting down server...")
        server.stop()
        print("Server stopped.")


if __name__ == "__main__":
    main()
