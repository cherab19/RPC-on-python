"""
RPC Stub - Client-side RPC proxy

Provides a Python-like interface to remote methods by handling
serialization, network communication, and response deserialization.
"""

from typing import Any, List, Dict, Optional, Callable, Type
from rpc_framework.transport.tcp_client import TCPClient
from rpc_framework.protocol import RPCRequest, RPCResponse
from rpc_framework.protocol.serializer import Serializer
from rpc_framework.utils import setup_logger

logger = setup_logger(__name__)


class RPCStub:
    """
    Client-side RPC stub.
    
    Provides a proxy interface to remote service methods.
    Handles serialization, network communication, and deserialization.
    """

    def __init__(
        self,
        client: TCPClient,
        service_name: str = "default",
        method_signatures: Dict[str, List[Type]] = None
    ):
        """
        Initialize RPC stub.
        
        Args:
            client: TCP client for communication
            service_name: Name of the remote service
            method_signatures: Optional method signatures for type validation
        """
        self.client = client
        self.service_name = service_name
        self.method_signatures = method_signatures or {}

    def invoke(self, method_name: str, params: List[Any], return_type: Type = None) -> Any:
        """
        Invoke a remote method.
        
        Args:
            method_name: Name of the remote method
            params: List of arguments to pass
            return_type: Expected return type (for deserialization)
            
        Returns:
            Deserialized method result
            
        Raises:
            RuntimeError: If RPC call fails
            ValueError: If response indicates error
        """
        try:
            # Create and send request
            request = RPCRequest.create(method_name, params, self.service_name)
            logger.debug(f"Invoking {self.service_name}.{method_name} with params {params}")

            request_dict = request.to_dict()
            response_dict = self.client.send_request(request_dict)

            # Parse response
            response = RPCResponse.from_dict(response_dict)

            if response.is_error():
                raise ValueError(f"Remote error: {response.error}")

            # Deserialize result
            if return_type:
                result = Serializer.deserialize(response.result, return_type)
            else:
                result = response.result

            logger.debug(f"Received result: {result}")
            return result

        except Exception as e:
            logger.error(f"RPC invocation failed: {e}")
            raise


class DynamicStub:
    """
    Dynamic stub that generates method proxies on the fly.
    
    Allows calling remote methods as if they were local Python methods.
    """

    def __init__(
        self,
        client: TCPClient,
        service_name: str = "default",
        method_signatures: Dict[str, List[Type]] = None
    ):
        """
        Initialize dynamic stub.
        
        Args:
            client: TCP client for communication
            service_name: Name of the remote service
            method_signatures: Optional method signatures
        """
        self.stub = RPCStub(client, service_name, method_signatures)

    def __getattr__(self, method_name: str) -> Callable:
        """
        Dynamically create a method proxy for remote method call.
        
        Args:
            method_name: Name of the remote method
            
        Returns:
            Callable that invokes the remote method
        """
        def method_proxy(*args: Any, **kwargs: Any) -> Any:
            if kwargs:
                raise ValueError("RPC does not support keyword arguments")
            return self.stub.invoke(method_name, list(args))

        return method_proxy
