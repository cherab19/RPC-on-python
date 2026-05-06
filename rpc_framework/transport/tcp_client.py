"""
TCP Client - Handles outgoing RPC connections and requests

Implements a TCP client that:
- Connects to RPC server
- Sends RPC requests
- Receives RPC responses
- Handles connection retries
"""

import socket
import json
import time
from typing import Dict, Any, Optional
from rpc_framework.utils import setup_logger, RetryStrategy, with_retry

logger = setup_logger(__name__)


class TCPClient:
    """
    TCP Client for RPC framework.
    
    Handles low-level socket communication for sending RPC requests
    and receiving responses. Supports retry logic for failed connections.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 5000, timeout: float = 5.0):
        """
        Initialize TCP client.
        
        Args:
            host: Server host address
            port: Server port number
            timeout: Socket timeout in seconds
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.socket: Optional[socket.socket] = None
        self.connected = False

    def connect(self) -> bool:
        """
        Connect to the RPC server.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.host, self.port))
            self.connected = True
            logger.info(f"Connected to server at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            self.connected = False
            return False

    @with_retry(strategy=RetryStrategy(max_attempts=3, initial_delay=0.1, max_delay=1.0))
    def send_request(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send RPC request and receive response.
        
        Implements at-least-once delivery semantics with automatic retries.
        
        Args:
            message: RPC request message
            
        Returns:
            Response message from server
            
        Raises:
            RuntimeError: If not connected or communication fails
        """
        if not self.connected:
            if not self.connect():
                raise RuntimeError("Failed to connect to server")

        try:
            # Send request
            self._send_message(message)
            logger.debug(f"Sent request: {message}")

            # Receive response
            response = self._receive_message()
            logger.debug(f"Received response: {response}")

            if response is None:
                raise RuntimeError("No response from server")

            return response

        except Exception as e:
            logger.error(f"Communication error: {e}")
            self.disconnect()
            raise

    def _send_message(self, message: Dict[str, Any]) -> None:
        """
        Send a message to socket with proper framing.
        
        Protocol: 4-byte length header (big-endian) + JSON message
        
        Args:
            message: Message dictionary to send
            
        Raises:
            RuntimeError: If send fails
        """
        try:
            message_data = json.dumps(message).encode("utf-8")
            length_data = len(message_data).to_bytes(4, byteorder="big")
            self.socket.sendall(length_data + message_data)
        except Exception as e:
            raise RuntimeError(f"Failed to send message: {e}")

    def _receive_message(self) -> Optional[Dict[str, Any]]:
        """
        Receive a message from socket with proper framing.
        
        Protocol: 4-byte length header (big-endian) + JSON message
        
        Returns:
            Parsed JSON message or None if connection closed
            
        Raises:
            RuntimeError: If receive fails
        """
        try:
            # Read 4-byte length header
            length_data = b""
            while len(length_data) < 4:
                chunk = self.socket.recv(4 - len(length_data))
                if not chunk:
                    return None
                length_data += chunk

            message_length = int.from_bytes(length_data, byteorder="big")

            # Read message body
            message_data = b""
            while len(message_data) < message_length:
                chunk = self.socket.recv(message_length - len(message_data))
                if not chunk:
                    return None
                message_data += chunk

            message = json.loads(message_data.decode("utf-8"))
            return message

        except socket.timeout:
            raise RuntimeError("Socket timeout")
        except Exception as e:
            raise RuntimeError(f"Failed to receive message: {e}")

    def disconnect(self) -> None:
        """Close the connection to the server."""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.connected = False
        logger.info("Disconnected from server")

    def is_connected(self) -> bool:
        """Check if client is currently connected."""
        return self.connected
