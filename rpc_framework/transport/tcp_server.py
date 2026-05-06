"""
TCP Server - Handles incoming RPC connections and requests

Implements a simple TCP server that:
- Listens on a specified host:port
- Accepts client connections
- Receives RPC messages
- Sends RPC responses
"""

import socket
import threading
import json
from typing import Callable, Optional, Dict, Any
from rpc_framework.utils import setup_logger

logger = setup_logger(__name__)


class TCPServer:
    """
    TCP Server for RPC framework.
    
    Handles low-level socket communication for receiving RPC requests
    and sending responses. Supports multi-threaded request handling.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 5000, max_connections: int = 5):
        """
        Initialize TCP server.
        
        Args:
            host: Server host address
            port: Server port number
            max_connections: Maximum number of backlogged connections
        """
        self.host = host
        self.port = port
        self.max_connections = max_connections
        self.socket: Optional[socket.socket] = None
        self.running = False
        self.server_thread: Optional[threading.Thread] = None
        self.request_handler: Optional[Callable] = None

    def start(self, request_handler: Callable[..., Dict[str, Any]]) -> None:
        """
        Start the TCP server in a background thread.
        
        Args:
            request_handler: Function to handle RPC requests
        """
        self.request_handler = request_handler
        self.running = True
        self.server_thread = threading.Thread(target=self._run, daemon=False)
        self.server_thread.start()
        logger.info(f"TCP Server started on {self.host}:{self.port}")

    def _run(self) -> None:
        """Main server loop - accept connections and handle requests."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(self.max_connections)
            logger.info(f"Listening on {self.host}:{self.port}")

            while self.running:
                try:
                    client_socket, client_addr = self.socket.accept()
                    logger.debug(f"Client connected from {client_addr}")
                    # Handle each client in a separate thread
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, client_addr),
                        daemon=True
                    )
                    client_thread.start()
                except OSError:
                    # Socket closed or server shutting down
                    break
        except Exception as e:
            logger.error(f"Server error: {e}")
        finally:
            self.stop()

    def _handle_client(self, client_socket: socket.socket, client_addr: tuple) -> None:
        """
        Handle a single client connection.
        
        Args:
            client_socket: Connected client socket
            client_addr: Client address tuple (host, port)
        """
        try:
            while self.running:
                # Receive message
                message = self._receive_message(client_socket)
                if not message:
                    break

                logger.debug(f"Received request: {message}")

                # Process request
                if self.request_handler:
                    response = self.request_handler(message)
                else:
                    response = {"error": "No request handler configured"}

                # Send response
                self._send_message(client_socket, response)
                logger.debug(f"Sent response: {response}")

        except Exception as e:
            logger.error(f"Client handler error: {e}")
        finally:
            client_socket.close()
            logger.debug(f"Client disconnected from {client_addr}")

    def _receive_message(self, sock: socket.socket) -> Optional[Dict[str, Any]]:
        """
        Receive a message from socket with proper framing.
        
        Protocol: 4-byte length header (big-endian) + JSON message
        
        Args:
            sock: Socket to receive from
            
        Returns:
            Parsed JSON message or None if connection closed
        """
        try:
            # Read 4-byte length header
            length_data = b""
            while len(length_data) < 4:
                chunk = sock.recv(4 - len(length_data))
                if not chunk:
                    return None
                length_data += chunk

            message_length = int.from_bytes(length_data, byteorder="big")

            # Read message body
            message_data = b""
            while len(message_data) < message_length:
                chunk = sock.recv(message_length - len(message_data))
                if not chunk:
                    return None
                message_data += chunk

            message = json.loads(message_data.decode("utf-8"))
            return message
        except Exception as e:
            logger.error(f"Error receiving message: {e}")
            return None

    def _send_message(self, sock: socket.socket, message: Dict[str, Any]) -> bool:
        """
        Send a message to socket with proper framing.
        
        Protocol: 4-byte length header (big-endian) + JSON message
        
        Args:
            sock: Socket to send to
            message: Message dictionary to send
            
        Returns:
            True if successful, False otherwise
        """
        try:
            message_data = json.dumps(message).encode("utf-8")
            length_data = len(message_data).to_bytes(4, byteorder="big")
            sock.sendall(length_data + message_data)
            return True
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False

    def stop(self) -> None:
        """Stop the server and close the socket."""
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        if self.server_thread:
            self.server_thread.join(timeout=5)
        logger.info("TCP Server stopped")

    def is_running(self) -> bool:
        """Check if server is currently running."""
        return self.running
