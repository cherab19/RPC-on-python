"""
IDL Parser - Parses Interface Definition Language files

Parses a simple IDL format to extract service definitions,
methods, parameters, and return types.
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from rpc_framework.utils import setup_logger

logger = setup_logger(__name__)


@dataclass
class Method:
    """Represents an RPC method definition."""
    name: str
    return_type: str
    params: List[Tuple[str, str]]  # List of (type, name) tuples

    def __repr__(self) -> str:
        params_str = ", ".join(f"{ptype} {pname}" for ptype, pname in self.params)
        return f"{self.return_type} {self.name}({params_str})"


@dataclass
class Service:
    """Represents an RPC service definition."""
    name: str
    methods: List[Method]


class IDLParser:
    """
    Parser for RPC Interface Definition Language.
    
    Parses a simple IDL format:
    
    service ServiceName {
        return_type method_name(param_type param_name, ...)
        ...
    }
    
    Supported types: int, string, float, bool, list
    """

    def __init__(self):
        """Initialize parser."""
        self.services: Dict[str, Service] = {}

    def parse_file(self, filename: str) -> Dict[str, Service]:
        """
        Parse an IDL file.
        
        Args:
            filename: Path to the IDL file
            
        Returns:
            Dictionary of service_name -> Service
            
        Raises:
            SyntaxError: If IDL syntax is invalid
        """
        with open(filename, 'r') as f:
            content = f.read()

        self.services = self.parse_content(content)
        return self.services

    def parse_content(self, content: str) -> Dict[str, Service]:
        """
        Parse IDL content from string.
        
        Args:
            content: IDL content as string
            
        Returns:
            Dictionary of service_name -> Service
            
        Raises:
            SyntaxError: If IDL syntax is invalid
        """
        services = {}

        # Find all service definitions
        service_pattern = r'service\s+(\w+)\s*\{([^}]+)\}'
        for match in re.finditer(service_pattern, content):
            service_name = match.group(1)
            service_body = match.group(2)

            try:
                service = self._parse_service(service_name, service_body)
                services[service_name] = service
                logger.debug(f"Parsed service: {service_name}")
            except Exception as e:
                raise SyntaxError(f"Error parsing service {service_name}: {e}")

        return services

    def _parse_service(self, service_name: str, body: str) -> Service:
        """Parse a service definition."""
        methods = []

        # Find all method definitions
        method_pattern = r'(\w+)\s+(\w+)\s*\(([^)]*)\)'
        for match in re.finditer(method_pattern, body):
            return_type = match.group(1)
            method_name = match.group(2)
            params_str = match.group(3)

            # Parse parameters
            params = self._parse_parameters(params_str)

            method = Method(method_name, return_type, params)
            methods.append(method)
            logger.debug(f"  Parsed method: {method}")

        if not methods:
            raise ValueError(f"Service {service_name} has no methods")

        return Service(service_name, methods)

    def _parse_parameters(self, params_str: str) -> List[Tuple[str, str]]:
        """Parse method parameters."""
        params = []
        if not params_str.strip():
            return params

        # Split by comma and parse each parameter
        for param in params_str.split(','):
            param = param.strip()
            parts = param.split()
            if len(parts) != 2:
                raise ValueError(f"Invalid parameter format: {param}")

            param_type, param_name = parts
            self._validate_type(param_type)
            params.append((param_type, param_name))

        return params

    def _validate_type(self, type_name: str) -> None:
        """Validate that type is supported."""
        supported_types = {'int', 'string', 'float', 'bool', 'list'}
        if type_name not in supported_types:
            raise ValueError(f"Unsupported type: {type_name}")

    def get_service(self, service_name: str) -> Optional[Service]:
        """Get a parsed service by name."""
        return self.services.get(service_name)

    def get_all_services(self) -> Dict[str, Service]:
        """Get all parsed services."""
        return dict(self.services)
