"""
Retry mechanism for at-least-once delivery semantics

Implements retry strategies for handling transient failures and
ensuring reliable RPC communication.
"""

import time
from typing import Callable, TypeVar, Any
from dataclasses import dataclass
from functools import wraps
from rpc_framework.utils.logger import setup_logger

logger = setup_logger(__name__)

T = TypeVar('T')


@dataclass
class RetryStrategy:
    """
    Configuration for retry behavior.
    
    Attributes:
        max_attempts: Maximum number of retry attempts
        initial_delay: Initial delay between retries (seconds)
        max_delay: Maximum delay between retries (seconds)
        backoff_factor: Multiplier for exponential backoff
    """
    max_attempts: int = 3
    initial_delay: float = 0.1
    max_delay: float = 5.0
    backoff_factor: float = 2.0

    def get_delay(self, attempt: int) -> float:
        """
        Calculate delay for given attempt number with exponential backoff.
        
        Args:
            attempt: Attempt number (0-indexed)
            
        Returns:
            Delay in seconds
        """
        delay = self.initial_delay * (self.backoff_factor ** attempt)
        return min(delay, self.max_delay)


def with_retry(strategy: RetryStrategy = None) -> Callable:
    """
    Decorator that adds retry logic to a function.
    
    Implements exponential backoff and automatic retries on failure.
    
    Args:
        strategy: RetryStrategy instance
        
    Returns:
        Decorated function with retry capability
        
    Example:
        @with_retry(strategy=RetryStrategy(max_attempts=3))
        def unreliable_function():
            pass
    """
    if strategy is None:
        strategy = RetryStrategy()

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception = None

            for attempt in range(strategy.max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < strategy.max_attempts - 1:
                        delay = strategy.get_delay(attempt)
                        logger.warning(
                            f"Attempt {attempt + 1}/{strategy.max_attempts} failed: {e}. "
                            f"Retrying in {delay:.2f}s..."
                        )
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"All {strategy.max_attempts} retry attempts failed: {e}"
                        )

            raise last_exception

        return wrapper

    return decorator
