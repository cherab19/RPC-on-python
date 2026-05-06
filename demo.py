"""
Comprehensive demo script that showcases the RPC framework

Runs both server and client in separate processes for demonstration.
"""

import subprocess
import time
import signal
import sys
from pathlib import Path

# Get the project root
PROJECT_ROOT = Path(__file__).parent.parent


def run_demo():
    """Run server and client demo."""
    print("\n" + "="*70)
    print("RPC FRAMEWORK DEMONSTRATION")
    print("="*70)

    # Start server in background
    print("\n[1] Starting server...")
    server_process = subprocess.Popen(
        [sys.executable, str(PROJECT_ROOT / "services/calculator/server.py")],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Give server time to start
    time.sleep(2)

    print("✓ Server started (PID: {})".format(server_process.pid))

    try:
        # Run client
        print("\n[2] Running client...")
        client_result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "services/calculator/client.py")],
            capture_output=False
        )

        print("\n[3] Client completed with exit code:", client_result.returncode)

    finally:
        # Stop server
        print("\n[4] Stopping server...")
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
            print("✓ Server stopped gracefully")
        except subprocess.TimeoutExpired:
            server_process.kill()
            print("✓ Server forcefully stopped")

    print("\n" + "="*70)
    print("Demo completed!")
    print("="*70 + "\n")


if __name__ == "__main__":
    try:
        run_demo()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
        sys.exit(1)
