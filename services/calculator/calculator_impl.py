"""
Calculator Service Implementation

Implements basic arithmetic operations: add, subtract, multiply, divide.
Also includes a simple greeting method.
"""

from rpc_framework.utils import setup_logger

logger = setup_logger(__name__)


class Calculator:
    """
    Calculator service implementation.
    
    Provides basic arithmetic operations with error handling.
    """

    def add(self, a: int, b: int) -> int:
        """Add two numbers."""
        logger.debug(f"add({a}, {b})")
        return a + b

    def subtract(self, a: int, b: int) -> int:
        """Subtract b from a."""
        logger.debug(f"subtract({a}, {b})")
        return a - b

    def multiply(self, a: int, b: int) -> int:
        """Multiply two numbers."""
        logger.debug(f"multiply({a}, {b})")
        return a * b

    def divide(self, a: int, b: int) -> int:
        """Divide a by b (integer division)."""
        logger.debug(f"divide({a}, {b})")
        if b == 0:
            raise ValueError("Division by zero")
        return a // b

    def greet(self, name: str) -> str:
        """Greet a person by name."""
        logger.debug(f"greet({name})")
        return f"Hello, {name}! Welcome to the Calculator Service."
