"""
RPC Message Protocol - Request and Response message definitions

Defines the message format for RPC communication:
- Request: method call with parameters
- Response: result or error
"""

from dataclasses import dataclass, asdict
from typing import Any, Optional, List
import time
import uuid


@dataclass
class RPCRequest:
    """
    RPC Request message.
    
    Attributes:
        request_id: Unique identifier for this request (for correlation and deduplication)
        method: Method name to invoke
        params: Method parameters (list of arguments)
        timestamp: Request creation timestamp (Unix time)
        service: Service name (optional, for routing)
    """
    request_id: str
    method: str
    params: List[Any]
    timestamp: float
    service: str = "default"

    @classmethod
    def create(cls, method: str, params: List[Any], service: str = "default") -> "RPCRequest":
        """
        Create a new RPC request with auto-generated ID and timestamp.
        
        Args:
            method: Method name to invoke
            params: Method parameters
            service: Service name
            
        Returns:
            New RPCRequest instance
        """
        return cls(
            request_id=str(uuid.uuid4()),
            method=method,
            params=params,
            timestamp=time.time(),
            service=service
        )

    def to_dict(self) -> dict:
        """Convert request to dictionary for serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "RPCRequest":
        """Create request from dictionary (deserialization)."""
        return cls(**data)


@dataclass
class RPCResponse:
    """
    RPC Response message.
    
    Attributes:
        request_id: Echoes the request ID for correlation
        result: Method result (if successful)
        error: Error message (if failed)
        timestamp: Response creation timestamp (Unix time)
    """
    request_id: str
    result: Optional[Any] = None
    error: Optional[str] = None
    timestamp: float = None

    def __post_init__(self):
        """Set timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = time.time()

    @classmethod
    def success(cls, request_id: str, result: Any) -> "RPCResponse":
        """
        Create a successful response.
        
        Args:
            request_id: Request ID to correlate with
            result: Method result
            
        Returns:
            New RPCResponse instance
        """
        return cls(request_id=request_id, result=result, error=None)

    @classmethod
    def error(cls, request_id: str, error_message: str) -> "RPCResponse":
        """
        Create an error response.
        
        Args:
            request_id: Request ID to correlate with
            error_message: Error description
            
        Returns:
            New RPCResponse instance
        """
        return cls(request_id=request_id, result=None, error=error_message)

    def is_success(self) -> bool:
        """Check if response indicates success."""
        return self.error is None

    def is_error(self) -> bool:
        """Check if response indicates error."""
        return self.error is not None

    def to_dict(self) -> dict:
        """Convert response to dictionary for serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "RPCResponse":
        """Create response from dictionary (deserialization)."""
        return cls(**data)
