"""
Logging utilities for RPC framework

Provides consistent logging across all modules.
"""

import logging
import sys


def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """
    Setup a logger instance with consistent formatting.
    
    Args:
        name: Logger name (typically __name__)
        level: Logging level (INFO, DEBUG, ERROR, etc.)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Only add handler if not already added (avoid duplicate logs)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    return logger
