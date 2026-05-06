"""
Serialization - Marshal and unmarshal RPC data

Implements type-safe serialization and deserialization with support for:
- Basic types: int, str, float, bool
- Collections: list, dict
- Type validation and conversion
"""

import json
from typing import Any, Type, List, Dict, get_type_hints, get_origin, get_args
from rpc_framework.utils import setup_logger

logger = setup_logger(__name__)


class Serializer:
    """
    Serializer for RPC messages.
    
    Handles marshaling (Python objects to JSON) and unmarshaling (JSON to Python objects)
    with type validation and conversion.
    """

    # Supported primitive types
    PRIMITIVE_TYPES = (int, str, float, bool, type(None))

    @staticmethod
    def serialize(obj: Any) -> Any:
        """
        Serialize Python object to JSON-compatible format.
        
        Args:
            obj: Object to serialize
            
        Returns:
            JSON-compatible value
            
        Raises:
            TypeError: If object type is not supported
        """
        if obj is None or isinstance(obj, (int, str, float, bool)):
            return obj

        elif isinstance(obj, list):
            return [Serializer.serialize(item) for item in obj]

        elif isinstance(obj, dict):
            return {k: Serializer.serialize(v) for k, v in obj.items()}

        elif isinstance(obj, (tuple, set)):
            return [Serializer.serialize(item) for item in obj]

        else:
            raise TypeError(f"Unsupported type for serialization: {type(obj).__name__}")

    @staticmethod
    def deserialize(data: Any, target_type: Type = None) -> Any:
        """
        Deserialize JSON data to Python object with optional type conversion.
        
        Args:
            data: JSON data to deserialize
            target_type: Expected type (for validation/conversion)
            
        Returns:
            Deserialized object
            
        Raises:
            ValueError: If type validation fails
            TypeError: If deserialization is not possible
        """
        # No type specified, return as-is
        if target_type is None:
            return data

        # Handle None type
        if data is None:
            if target_type == type(None):
                return None
            return None  # Accept None for optional types

        # Handle primitive types
        if target_type in Serializer.PRIMITIVE_TYPES:
            if not isinstance(data, target_type):
                try:
                    return target_type(data)
                except (ValueError, TypeError):
                    raise ValueError(f"Cannot convert {data} to {target_type.__name__}")
            return data

        # Handle list
        if target_type == list or get_origin(target_type) == list:
            if not isinstance(data, list):
                raise ValueError(f"Expected list, got {type(data).__name__}")

            # Get element type if available
            args = get_args(target_type)
            element_type = args[0] if args else None

            return [Serializer.deserialize(item, element_type) for item in data]

        # Handle dict
        if target_type == dict or get_origin(target_type) == dict:
            if not isinstance(data, dict):
                raise ValueError(f"Expected dict, got {type(data).__name__}")
            return data

        raise TypeError(f"Unsupported target type: {target_type}")

    @staticmethod
    def validate_types(values: List[Any], expected_types: List[Type]) -> bool:
        """
        Validate that values match expected types.
        
        Args:
            values: Values to validate
            expected_types: Expected types for each value
            
        Returns:
            True if all types match
            
        Raises:
            ValueError: If type validation fails
        """
        if len(values) != len(expected_types):
            raise ValueError(
                f"Parameter count mismatch: got {len(values)}, expected {len(expected_types)}"
            )

        for i, (value, expected_type) in enumerate(zip(values, expected_types)):
            try:
                Serializer.deserialize(value, expected_type)
            except (ValueError, TypeError) as e:
                raise ValueError(f"Parameter {i} type mismatch: {e}")

        return True

    @staticmethod
    def to_json(obj: Any) -> str:
        """
        Convert object to JSON string.
        
        Args:
            obj: Object to convert
            
        Returns:
            JSON string
        """
        return json.dumps(Serializer.serialize(obj))

    @staticmethod
    def from_json(json_str: str, target_type: Type = None) -> Any:
        """
        Parse JSON string to Python object.
        
        Args:
            json_str: JSON string to parse
            target_type: Expected type for conversion
            
        Returns:
            Parsed object
        """
        data = json.loads(json_str)
        return Serializer.deserialize(data, target_type)
