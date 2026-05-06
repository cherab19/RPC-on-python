"""
Calculator Client

Demonstrates RPC client usage by calling remote Calculator service methods.
"""

import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from rpc_framework.transport.tcp_client import TCPClient
from rpc_framework.runtime.stub import RPCStub
from rpc_framework.utils import setup_logger

logger = setup_logger(__name__, "INFO")


def main():
    """Run calculator client examples."""
    print("\n" + "="*60)
    print("Calculator RPC Client")
    print("="*60 + "\n")

    try:
        # Connect to server
        print("Connecting to server at 127.0.0.1:5000...")
        client = TCPClient(host="127.0.0.1", port=5000, timeout=5.0)

        if not client.connect():
            print("✗ Failed to connect to server")
            return

        print("✓ Connected to server\n")

        # Create stub
        stub = RPCStub(client, service_name="Calculator")

        # Test cases
        test_cases = [
            ("add", [5, 3], int, "5 + 3"),
            ("subtract", [10, 4], int, "10 - 4"),
            ("multiply", [6, 7], int, "6 × 7"),
            ("divide", [20, 4], int, "20 ÷ 4"),
            ("greet", ["Alice"], str, 'greet("Alice")'),
            ("add", [100, 200], int, "100 + 200"),
        ]

        print("Running test cases:\n")
        for method, params, return_type, description in test_cases:
            try:
                result = stub.invoke(method, params, return_type)
                print(f"✓ {description:20} = {result}")
            except Exception as e:
                print(f"✗ {description:20} ERROR: {e}")

        # Test error case - division by zero
        print("\nTesting error handling:")
        try:
            result = stub.invoke("divide", [10, 0], int)
            print(f"✗ divide(10, 0) should have failed!")
        except ValueError as e:
            print(f"✓ divide(10, 0) correctly raised error: {e}")

        # Close connection
        client.disconnect()
        print("\n✓ Connection closed")

        print("\n" + "="*60)
        print("All tests completed!")
        print("="*60 + "\n")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        logger.error(f"Client error: {e}", exc_info=True)


if __name__ == "__main__":
    main()
