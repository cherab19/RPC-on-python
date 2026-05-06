"""
RPC Skeleton - Server-side request dispatcher

Receives RPC requests, dispatches to the appropriate service method,
and returns responses. Handles error cases and at-least-once semantics.
"""

from typing import Dict, Any, Callable, Optional
from rpc_framework.protocol import RPCRequest, RPCResponse
from rpc_framework.runtime.registry import ServiceRegistry
from rpc_framework.protocol.serializer import Serializer
from rpc_framework.utils import setup_logger

logger = setup_logger(__name__)


class RPCSkeleton:
    """
    Server-side RPC dispatcher (skeleton).
    
    Receives serialized RPC requests from the transport layer,
    dispatches to appropriate service methods, and returns serialized responses.
    """

    def __init__(self, registry: ServiceRegistry):
        """
        Initialize skeleton with service registry.
        
        Args:
            registry: ServiceRegistry containing service implementations
        """
        self.registry = registry
        self._processed_requests: Dict[str, Any] = {}  # For deduplication

    def dispatch_request(self, request_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dispatch an RPC request to the appropriate service method.
        
        Implements at-least-once semantics by caching results for duplicate requests.
        
        Args:
            request_dict: Serialized RPC request
            
        Returns:
            Serialized RPC response
        """
        try:
            # Deserialize request
            request = RPCRequest.from_dict(request_dict)
            logger.debug(f"Dispatching request {request.request_id}: {request.method}")

            # Check for duplicate request (at-least-once semantics)
            if request.request_id in self._processed_requests:
                logger.info(f"Duplicate request detected: {request.request_id}, returning cached result")
                return self._processed_requests[request.request_id]

            # Dispatch to service method
            response = self._execute_method(request)

            # Cache result for deduplication
            response_dict = response.to_dict()
            self._processed_requests[request.request_id] = response_dict

            return response_dict

        except Exception as e:
            logger.error(f"Dispatch error: {e}")
            # Create error response
            return RPCResponse.error(
                request_id=request_dict.get("request_id", "unknown"),
                error_message=str(e)
            ).to_dict()

    def _execute_method(self, request: RPCRequest) -> RPCResponse:
        """
        Execute a service method.
        
        Args:
            request: RPC request
            
        Returns:
            RPC response
        """
        try:
            # Get method from registry
            service_name = request.service
            method_name = request.method

            if not self.registry.has_service(service_name):
                raise ValueError(f"Service not found: {service_name}")

            if not self.registry.has_method(service_name, method_name):
                raise ValueError(f"Method not found: {service_name}.{method_name}")

            method = self.registry.get_method(service_name, method_name)

            # Validate and deserialize parameters
            signature = self.registry.get_signature(service_name, method_name)
            if signature:
                try:
                    Serializer.validate_types(request.params, signature)
                except ValueError as e:
                    return RPCResponse.error(request.request_id, f"Parameter validation failed: {e}")

                # Deserialize parameters
                params = [
                    Serializer.deserialize(param, sig_type)
                    for param, sig_type in zip(request.params, signature)
                ]
            else:
                params = request.params

            # Execute method
            logger.debug(f"Executing {service_name}.{method_name} with params {params}")
            result = method(*params)

            # Serialize result
            serialized_result = Serializer.serialize(result)

            return RPCResponse.success(request.request_id, serialized_result)

        except Exception as e:
            logger.error(f"Method execution failed: {e}")
            return RPCResponse.error(request.request_id, str(e))

    def clear_cache(self) -> None:
        """Clear the processed requests cache."""
        self._processed_requests.clear()
