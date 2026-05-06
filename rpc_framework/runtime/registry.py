"""
Service Registry - Stores and manages RPC service implementations

Maintains a mapping of service names to method implementations,
enabling dynamic method dispatch on the server side.
"""

from typing import Dict, Callable, Any, List, Type
from rpc_framework.utils import setup_logger

logger = setup_logger(__name__)


class ServiceRegistry:
    """
    Registry for RPC services and their methods.
    
    Allows registration of service implementations and provides
    lookup capabilities for method dispatch during request handling.
    """

    def __init__(self):
        """Initialize empty service registry."""
        self._services: Dict[str, Any] = {}
        self._methods: Dict[str, Dict[str, Callable]] = {}
        self._signatures: Dict[str, Dict[str, List[Type]]] = {}

    def register_service(
        self,
        service_name: str,
        implementation: Any,
        methods: Dict[str, Callable],
        signatures: Dict[str, List[Type]] = None
    ) -> None:
        """
        Register a service implementation.
        
        Args:
            service_name: Name of the service
            implementation: Service implementation instance
            methods: Dictionary of method_name -> callable
            signatures: Optional method signatures for type validation
        """
        self._services[service_name] = implementation
        self._methods[service_name] = methods
        self._signatures[service_name] = signatures or {}
        logger.info(f"Registered service: {service_name} with {len(methods)} methods")

    def get_method(self, service_name: str, method_name: str) -> Callable:
        """
        Get a method from a registered service.
        
        Args:
            service_name: Service name
            method_name: Method name
            
        Returns:
            Callable method
            
        Raises:
            KeyError: If service or method not found
        """
        if service_name not in self._services:
            raise KeyError(f"Service not found: {service_name}")

        if method_name not in self._methods[service_name]:
            raise KeyError(f"Method not found: {service_name}.{method_name}")

        return self._methods[service_name][method_name]

    def get_signature(self, service_name: str, method_name: str) -> List[Type]:
        """
        Get method signature (parameter types).
        
        Args:
            service_name: Service name
            method_name: Method name
            
        Returns:
            List of parameter types
        """
        if service_name in self._signatures:
            return self._signatures[service_name].get(method_name, [])
        return []

    def has_service(self, service_name: str) -> bool:
        """Check if service is registered."""
        return service_name in self._services

    def has_method(self, service_name: str, method_name: str) -> bool:
        """Check if method exists in service."""
        if service_name not in self._methods:
            return False
        return method_name in self._methods[service_name]

    def get_services(self) -> Dict[str, Any]:
        """Get all registered services."""
        return dict(self._services)

    def get_methods(self, service_name: str) -> Dict[str, Callable]:
        """Get all methods for a service."""
        return self._methods.get(service_name, {})
